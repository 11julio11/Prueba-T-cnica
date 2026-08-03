from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_rds as rds,
    aws_sqs as sqs,
    aws_secretsmanager as secretsmanager,
    SecretValue,
    CfnOutput
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
        db_instance = rds.DatabaseInstance(
            self, "PostgresDB",
            engine=rds.DatabaseInstanceEngine.postgres(version=rds.PostgresEngineVersion.VER_15),
            vpc=vpc,
            credentials=rds.Credentials.from_secret(db_secret),
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            instance_type=ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.MICRO),
            allocated_storage=20,
            max_allocated_storage=50,
            database_name="requests_db"
        )

        # 4. ECS Cluster
        cluster = ecs.Cluster(
            self, "AppCluster",
            vpc=vpc,
            cluster_name="requests-cluster"
        )

        # Allow ECS tasks to access the Database
        db_instance.connections.allow_from(
            ec2.Peer.ipv4(vpc.vpc_cidr_block),
            ec2.Port.tcp(5432),
            "Allow connection from ECS Tasks"
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
                    "POSTGRES_DB": "requests_db",
                    "POSTGRES_HOST": db_instance.db_instance_endpoint_address
                },
                secrets={
                    "POSTGRES_USER": ecs.Secret.from_secrets_manager(db_secret, "username"),
                    "POSTGRES_PASSWORD": ecs.Secret.from_secrets_manager(db_secret, "password")
                }
            ),
            task_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            public_load_balancer=True
        )

        # Grant permissions
        db_secret.grant_read(backend_service.task_definition.task_role)

        # 6. Consumer Application (Worker via Fargate)
        consumer_task = ecs.FargateTaskDefinition(
            self, "ConsumerTaskDef",
            cpu=256,
            memory_limit_mib=512
        )
        
        consumer_task.add_container("ConsumerContainer",
            image=ecs.ContainerImage.from_asset("../../", file="consumer/Dockerfile"),
            environment={
                "POSTGRES_DB": "requests_db",
                "POSTGRES_HOST": db_instance.db_instance_endpoint_address,
                "API_BASE_URL": "http://" + backend_service.load_balancer.load_balancer_dns_name + "/api/v1"
            },
            secrets={
                "POSTGRES_USER": ecs.Secret.from_secrets_manager(db_secret, "username"),
                "POSTGRES_PASSWORD": ecs.Secret.from_secrets_manager(db_secret, "password")
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

        # Grant permissions to consumer
        db_secret.grant_read(consumer_task.task_role)

        # Outputs
        CfnOutput(self, "ApiUrl", value=backend_service.load_balancer.load_balancer_dns_name)
        CfnOutput(self, "DatabaseEndpoint", value=db_instance.db_instance_endpoint_address)
