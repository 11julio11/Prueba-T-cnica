# Arquitectura y Despliegue en AWS (IaC)

La infraestructura de la aplicación está definida como código (Infrastructure as Code) utilizando **AWS CDK con Python**. Esto asegura que el despliegue sea reproducible, seguro y escalable.

## Flujograma de Arquitectura

El siguiente diagrama muestra el flujo completo de una solicitud desde el usuario hasta la capa de datos, incluyendo los controles de seguridad y observabilidad transversales.

```mermaid
flowchart TD
    Usuario(["👤 Usuario"])
    Frontend(["🖥️ Frontend\nS3 + CloudFront"])
    HTTPS["🔒 HTTPS + Bearer Token\nJWT / Cognito"]
    WAF["🛡️ AWS WAF\nDNS · Route 53\nDDoS protection"]
    ALB["⚖️ Application Load Balancer\nSSL Termination · Health Checks"]

    subgraph ECS ["☁️ ECS Fargate — Private Subnet"]
        SvcBackend["⚙️ Servicio Backend\nFastAPI"]
        SvcConsumer["📨 Servicio Consumer\nBackground Worker"]
        SvcOthers["... Otros servicios"]
    end

    SQS[("📬 AWS SQS\nMessage Queue")]
    DB[("🗄️ RDS PostgreSQL\nPrivate Subnet")]

    subgraph CrossCutting ["🔧 Servicios Transversales"]
        Secrets["🔑 AWS Secrets Manager\nCredenciales · API keys"]
        Logs["📊 CloudWatch\nLogs · Métricas · Alertas"]
        Tracing["🔍 AWS X-Ray\nTrazabilidad distribuida"]
    end

    Usuario -->|"Interacción"| Frontend
    Frontend -->|"HTTPS + Token"| HTTPS
    HTTPS --> WAF
    WAF -->|"Tráfico limpio"| ALB
    ALB --> SvcBackend
    ALB -.->|"Escalado horizontal"| SvcOthers

    SvcBackend -->|"Escritura / Lectura"| DB
    SvcBackend -->|"Publica eventos"| SQS
    SQS -->|"Consume mensajes"| SvcConsumer

    SvcBackend <-->|"Lee secretos"| Secrets
    SvcConsumer <-->|"Lee secretos"| Secrets

    SvcBackend -->|"Emite logs y métricas"| Logs
    SvcConsumer -->|"Emite logs y métricas"| Logs
    SvcBackend -->|"Traza requests"| Tracing
    SvcConsumer -->|"Traza requests"| Tracing

    style ECS fill:#1a1a2e,stroke:#4f46e5,color:#fff
    style CrossCutting fill:#0f2027,stroke:#059669,color:#fff
    style DB fill:#1e3a5f,stroke:#3b82f6,color:#fff
    style SQS fill:#1e3a5f,stroke:#3b82f6,color:#fff
    style WAF fill:#3b0764,stroke:#a855f7,color:#fff
    style ALB fill:#1c1917,stroke:#f59e0b,color:#fff
```

### Descripción de Componentes

| Capa | Componente AWS | Responsabilidad |
|------|---------------|-----------------|
| **Presentación** | S3 + CloudFront | Sirve el frontend estático con CDN global |
| **Autenticación** | Amazon Cognito / JWT | Emite y valida tokens de acceso |
| **Protección perimetral** | Route 53 + AWS WAF | DNS, protección DDoS y filtrado de tráfico malicioso |
| **Balanceo** | Application Load Balancer | Termina SSL y distribuye tráfico entre tareas ECS |
| **Cómputo** | ECS Fargate | Ejecuta los servicios como contenedores serverless |
| **Mensajería** | AWS SQS | Desacopla el backend del worker (reemplaza RabbitMQ) |
| **Base de datos** | RDS PostgreSQL | Base de datos gestionada en subred privada |
| **Secretos** | AWS Secrets Manager | Almacena credenciales de BD, API keys y tokens |
| **Observabilidad** | CloudWatch | Centraliza logs, métricas y alarmas |
| **Trazabilidad** | AWS X-Ray | Rastrea el flujo de cada request entre servicios |

---

## Instrucciones de Despliegue (CDK)

El código de infraestructura se encuentra en la carpeta `infrastructure/aws`.

### Prerrequisitos
- AWS CLI configurado (`aws configure`)
- Node.js instalado + CDK global: `npm install -g aws-cdk`
- Python 3.12+

### Pasos para Desplegar

1. Crear el entorno virtual e instalar dependencias:
   ```bash
   cd infrastructure/aws
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Bootstrap de CDK (una sola vez por cuenta/región):
   ```bash
   cdk bootstrap
   ```

3. Revisar los cambios antes de aplicar:
   ```bash
   cdk diff
   ```

4. Desplegar la infraestructura completa:
   ```bash
   cdk deploy
   ```

Al finalizar, CDK imprime el **Endpoint del Load Balancer** (URL pública de la API).
