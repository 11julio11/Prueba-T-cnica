from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_rds as rds,
    aws_secretsmanager as secretsmanager,
    SecretValue,
    CfnOutput,
    RemovalPolicy
)
from constructs import Construct

class InfrastructureStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 1. VPC Configuration
        vpc = ec2.Vpc(
            self, "ServiceRequestsVpc",
            max_azs=2,
            nat_gateways=1
        )

        # Define strict SG: only backend can connect
        db_sg = ec2.SecurityGroup(
            self,
            "DatabaseSG",
            vpc=vpc,
            description="Allow backend to connect to RDS",
            allow_all_outbound=True,
        )

        # 3. RDS PostgreSQL Database
        # Secret for DB Credentials
        db_secret = secretsmanager.Secret(
            self, "DBCredentials",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template='{"username": "postgres"}',
                generate_string_key="password",
                exclude_characters="\"@/\\"
            )
        )

        # DB Instance
        database = rds.DatabaseInstance(
            self,
            "RequestsDB",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_15
            ),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.T3, ec2.InstanceSize.MICRO
            ),
            vpc=vpc,
            security_groups=[db_sg],
            credentials=rds.Credentials.from_secret(db_secret),
            database_name="solicitudes_db",
            storage_encrypted=True,
            removal_policy=RemovalPolicy.DESTROY
        )

        # 4. ECS Cluster
        cluster = ecs.Cluster(
            self, "AppCluster",
            vpc=vpc,
            cluster_name="requests-cluster"
        )

        from aws_cdk import aws_certificatemanager as acm
        dummy_cert = acm.Certificate.from_certificate_arn(
            self, "DummyCert", 
            "arn:aws:acm:us-east-1:123456789012:certificate/dummy-cert"
        )

        # 5. Backend Application (API via Fargate with Application Load Balancer)
        backend_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self, "BackendService",
            cluster=cluster,
            cpu=256,
            memory_limit_mib=512,
            desired_count=2,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_asset("../../", file="backend/Dockerfile"),
                container_port=8000,
                environment={
                    "POSTGRES_DB": "solicitudes_db",
                    "POSTGRES_HOST": database.db_instance_endpoint_address
                },
                secrets={
                    "POSTGRES_USER": ecs.Secret.from_secrets_manager(db_secret, "username"),
                    "POSTGRES_PASSWORD": ecs.Secret.from_secrets_manager(db_secret, "password")
                }
            ),
            task_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            public_load_balancer=True,
            certificate=dummy_cert,
            redirect_http=True
        )

        backend_sg = backend_service.service.connections.security_groups[0]
        db_sg.add_ingress_rule(
            peer=backend_sg,
            connection=ec2.Port.tcp(5432),
            description="Allow backend to connect to RDS",
        )

        backend_service.target_group.configure_health_check(
            path="/health"
        )

        # Grant permissions
        db_secret.grant_read(backend_service.task_definition.task_role)

        # 6. Consumer Application (Worker via Fargate)
        consumer_task = ecs.FargateTaskDefinition(
            self, "ConsumerTaskDef",
            cpu=256,
            memory_limit_mib=512
        )
        
        # WARNING: Using HTTP listener for the ALB as requested by the architecture diagram.
        # In a production environment, this MUST be HTTPS (port 443) with a valid SSL/TLS certificate.
        
        consumer_task.add_container("ConsumerContainer",
            image=ecs.ContainerImage.from_asset("../../", file="consumer/Dockerfile"),
            environment={
                "API_BASE_URL": "http://" + backend_service.load_balancer.load_balancer_dns_name + "/api/v1"
            },
            logging=ecs.LogDrivers.aws_logs(stream_prefix="ConsumerLog")
        )

        consumer_service = ecs.FargateService(
            self, "ConsumerService",
            cluster=cluster,
            task_definition=consumer_task,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            desired_count=1
        )

        # Outputs
        CfnOutput(self, "ApiUrl", value=backend_service.load_balancer.load_balancer_dns_name)
        CfnOutput(self, "DatabaseEndpoint", value=database.db_instance_endpoint_address)
