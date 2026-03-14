from strands import tool


# Base de datos de instancias EC2 (características y precios aproximados en USD/hora, región us-east-1)
EC2_INSTANCIAS = {
    "t3.nano": {"vcpus": 2, "ram_gb": 0.5, "precio_hora": 0.0052},
    "t3.micro": {"vcpus": 2, "ram_gb": 1, "precio_hora": 0.0104},
    "t3.small": {"vcpus": 2, "ram_gb": 2, "precio_hora": 0.0208},
    "t3.medium": {"vcpus": 2, "ram_gb": 4, "precio_hora": 0.0416},
    "t3.large": {"vcpus": 2, "ram_gb": 8, "precio_hora": 0.0832},
    "t3.xlarge": {"vcpus": 4, "ram_gb": 16, "precio_hora": 0.1664},
    "t3.2xlarge": {"vcpus": 8, "ram_gb": 32, "precio_hora": 0.3328},
    "t4g.nano": {"vcpus": 2, "ram_gb": 0.5, "precio_hora": 0.0042},
    "t4g.micro": {"vcpus": 2, "ram_gb": 1, "precio_hora": 0.0084},
    "t4g.small": {"vcpus": 2, "ram_gb": 2, "precio_hora": 0.0168},
    "t4g.medium": {"vcpus": 2, "ram_gb": 4, "precio_hora": 0.0336},
    "m5.large": {"vcpus": 2, "ram_gb": 8, "precio_hora": 0.096},
    "m5.xlarge": {"vcpus": 4, "ram_gb": 16, "precio_hora": 0.192},
    "m5.2xlarge": {"vcpus": 8, "ram_gb": 32, "precio_hora": 0.384},
    "m6i.large": {"vcpus": 2, "ram_gb": 8, "precio_hora": 0.096},
    "m6i.xlarge": {"vcpus": 4, "ram_gb": 16, "precio_hora": 0.192},
    "c5.large": {"vcpus": 2, "ram_gb": 4, "precio_hora": 0.085},
    "c5.xlarge": {"vcpus": 4, "ram_gb": 8, "precio_hora": 0.17},
    "c6i.large": {"vcpus": 2, "ram_gb": 4, "precio_hora": 0.085},
    "c6i.xlarge": {"vcpus": 4, "ram_gb": 8, "precio_hora": 0.17},
}


@tool
def comparar_instancias_ec2(instancia1: str, instancia2: str) -> str:
    """
    Compara dos tipos de instancia EC2 mostrando sus características principales.

    Args:
        instancia1: Tipo de instancia EC2 (ej: t3.micro, m5.large).
        instancia2: Tipo de instancia EC2 (ej: t3.small, m5.xlarge).

    Returns:
        Comparación detallada de vCPUs, RAM y precio aproximado por hora.
    """
    inst1 = instancia1.lower().strip()
    inst2 = instancia2.lower().strip()

    if inst1 not in EC2_INSTANCIAS:
        instancias_validas = ", ".join(sorted(EC2_INSTANCIAS.keys()))
        return f"Instancia '{instancia1}' no encontrada.\nInstancias disponibles: {instancias_validas}"

    if inst2 not in EC2_INSTANCIAS:
        instancias_validas = ", ".join(sorted(EC2_INSTANCIAS.keys()))
        return f"Instancia '{instancia2}' no encontrada.\nInstancias disponibles: {instancias_validas}"

    datos1 = EC2_INSTANCIAS[inst1]
    datos2 = EC2_INSTANCIAS[inst2]

    # Calcular diferencias
    diff_vcpus = datos2["vcpus"] - datos1["vcpus"]
    diff_ram = datos2["ram_gb"] - datos1["ram_gb"]
    diff_precio = datos2["precio_hora"] - datos1["precio_hora"]
    pct_precio = (diff_precio / datos1["precio_hora"] * 100) if datos1["precio_hora"] > 0 else 0

    resultado = (
        f"Comparación de instancias EC2 (región us-east-1):\n"
        f"\n{'Característica':<20} {inst1.upper():<15} {inst2.upper():<15} {'Diferencia':<15}\n"
        f"{'-'*65}\n"
        f"{'vCPUs':<20} {datos1['vcpus']:<15} {datos2['vcpus']:<15} "
        f"{f'+{diff_vcpus}' if diff_vcpus > 0 else diff_vcpus}\n"
        f"{'RAM (GB)':<20} {datos1['ram_gb']:<15} {datos2['ram_gb']:<15} "
        f"{f'+{diff_ram}' if diff_ram > 0 else diff_ram}\n"
        f"{'Precio/hora (USD)':<20} ${datos1['precio_hora']:<14.4f} ${datos2['precio_hora']:<14.4f} "
        f"{f'+${diff_precio:.4f}' if diff_precio > 0 else f'-${abs(diff_precio):.4f}'} ({pct_precio:+.1f}%)\n"
        f"\nCosto mensual estimado (730 horas):\n"
        f"  {inst1.upper()}: ${datos1['precio_hora'] * 730:.2f}\n"
        f"  {inst2.upper()}: ${datos2['precio_hora'] * 730:.2f}"
    )

    return resultado


@tool
def estimar_costo_lambda(
    invocaciones: int,
    duracion_ms: float,
    memoria_mb: int,
) -> str:
    """
    Calcula el costo mensual estimado de AWS Lambda.

    Args:
        invocaciones: Número de invocaciones por mes.
        duracion_ms: Duración promedio de cada invocación en milisegundos.
        memoria_mb: Memoria asignada a la función en MB (128 a 10240).

    Returns:
        Desglose del costo mensual estimado en USD.
    """
    PRECIO_POR_SOLICITUD = 0.20 / 1_000_000        # USD por invocación
    PRECIO_POR_GB_SEGUNDO = 0.0000166667            # USD por GB-segundo

    costo_solicitudes = invocaciones * PRECIO_POR_SOLICITUD
    gb_segundos = (memoria_mb / 1024) * (duracion_ms / 1000) * invocaciones
    costo_computo = gb_segundos * PRECIO_POR_GB_SEGUNDO
    total = costo_solicitudes + costo_computo

    return (
        f"Estimación mensual AWS Lambda:\n"
        f"  Invocaciones:      {invocaciones:,}\n"
        f"  Duración promedio: {duracion_ms} ms\n"
        f"  Memoria:           {memoria_mb} MB\n"
        f"  Costo solicitudes: ${costo_solicitudes:.4f}\n"
        f"  Costo cómputo:     ${costo_computo:.4f}\n"
        f"  Total estimado:    ${total:.4f} USD/mes"
    )


@tool
def recomendar_arquitectura(caso_de_uso: str) -> str:
    """
    Devuelve una arquitectura AWS recomendada según el caso de uso.

    Args:
        caso_de_uso: Tipo de aplicación. Valores válidos:
                     api_rest, streaming, ml_inference, static_web, batch.

    Returns:
        Descripción de la arquitectura recomendada con los servicios AWS sugeridos.
    """
    arquitecturas: dict[str, str] = {
        "api_rest": (
            "API REST — Arquitectura serverless recomendada:\n"
            "  • API Gateway (HTTP API) → Lambda → DynamoDB\n"
            "  • CloudFront para caché de respuestas\n"
            "  • Cognito para autenticación\n"
            "  • CloudWatch para monitoreo"
        ),
        "streaming": (
            "Streaming de datos — Arquitectura recomendada:\n"
            "  • Kinesis Data Streams (ingesta)\n"
            "  • Kinesis Data Firehose (entrega a S3/Redshift)\n"
            "  • Lambda para transformaciones en tiempo real\n"
            "  • OpenSearch Service para búsqueda y visualización"
        ),
        "ml_inference": (
            "ML Inference — Arquitectura recomendada:\n"
            "  • SageMaker Endpoints (inferencia en tiempo real)\n"
            "  • API Gateway + Lambda como proxy\n"
            "  • S3 para almacenar modelos y artefactos\n"
            "  • ECR para imágenes de contenedor personalizadas"
        ),
        "static_web": (
            "Sitio web estático — Arquitectura recomendada:\n"
            "  • S3 (alojamiento de archivos estáticos)\n"
            "  • CloudFront (CDN global)\n"
            "  • Route 53 (DNS)\n"
            "  • ACM (certificado SSL/TLS gratuito)"
        ),
        "batch": (
            "Procesamiento batch — Arquitectura recomendada:\n"
            "  • AWS Batch (orquestación de jobs)\n"
            "  • S3 para datos de entrada/salida\n"
            "  • Step Functions para flujos complejos\n"
            "  • EventBridge Scheduler para ejecución programada"
        ),
    }

    caso = caso_de_uso.lower().strip()
    if caso not in arquitecturas:
        opciones = ", ".join(arquitecturas.keys())
        return f"Caso de uso '{caso_de_uso}' no reconocido. Opciones válidas: {opciones}"

    return arquitecturas[caso]


@tool
def buscar_servicio_aws(categoria: str) -> str:
    """
    Lista los principales servicios AWS según la categoría indicada.

    Args:
        categoria: Categoría de servicios. Valores válidos:
                   compute, storage, database, ai, networking.

    Returns:
        Lista de servicios AWS con una breve descripción de cada uno.
    """
    servicios: dict[str, list[tuple[str, str]]] = {
        "compute": [
            ("EC2", "Máquinas virtuales escalables"),
            ("Lambda", "Funciones serverless por evento"),
            ("ECS", "Contenedores gestionados con Docker"),
            ("EKS", "Kubernetes gestionado"),
            ("Fargate", "Cómputo serverless para contenedores"),
        ],
        "storage": [
            ("S3", "Almacenamiento de objetos ilimitado"),
            ("EBS", "Discos de bloque para EC2"),
            ("EFS", "Sistema de archivos NFS gestionado"),
            ("Glacier", "Archivado de datos de bajo costo"),
            ("FSx", "Sistemas de archivos de alto rendimiento"),
        ],
        "database": [
            ("RDS", "Bases de datos relacionales gestionadas"),
            ("DynamoDB", "Base de datos NoSQL serverless"),
            ("Aurora", "MySQL/PostgreSQL de alto rendimiento"),
            ("ElastiCache", "Caché en memoria con Redis/Memcached"),
            ("Redshift", "Data warehouse para analítica"),
        ],
        "ai": [
            ("Bedrock", "Modelos fundacionales de IA generativa"),
            ("SageMaker", "Plataforma completa de ML"),
            ("Rekognition", "Análisis de imágenes y video"),
            ("Comprehend", "Procesamiento de lenguaje natural"),
            ("Textract", "Extracción de texto de documentos"),
        ],
        "networking": [
            ("VPC", "Red privada virtual aislada"),
            ("CloudFront", "CDN global de baja latencia"),
            ("Route 53", "DNS escalable y de alta disponibilidad"),
            ("API Gateway", "Gestión de APIs REST y WebSocket"),
            ("Direct Connect", "Conexión dedicada a AWS"),
        ],
    }

    cat = categoria.lower().strip()
    if cat not in servicios:
        opciones = ", ".join(servicios.keys())
        return f"Categoría '{categoria}' no reconocida. Opciones válidas: {opciones}"

    lista = servicios[cat]
    resultado = f"Servicios AWS — {cat.upper()}:\n"
    resultado += "\n".join(f"  • {nombre}: {desc}" for nombre, desc in lista)
    return resultado
