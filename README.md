# CloudArquitecto - Agente AWS

Agente conversacional especializado en arquitectura y costos de AWS, construido con [Strands Agents](https://strandsagents.com).

## Descripción

CloudArquitecto es un asistente inteligente que ayuda a:
- Comparar instancias EC2 y analizar diferencias de costo
- Estimar costos de funciones AWS Lambda
- Recomendar arquitecturas AWS según el caso de uso
- Buscar y explorar servicios AWS por categoría
- Realizar cálculos y consultas en tiempo real

## Requisitos

- Python 3.10+
- Credenciales de AWS Bedrock (proveedor por defecto) u otro LLM soportado

## Instalación

```bash
pip install -r requirements.txt
```

## Uso

Inicia el agente interactivo:

```bash
python agent.py
```

Luego interactúa escribiendo consultas en español:

```
Tu: Compara t3.micro con t3.small
Tu: ¿Cuánto cuesta una Lambda con 512MB, 100ms y 1M invocaciones?
Tu: Recomienda una arquitectura para una API REST
Tu: Busca servicios de compute
Tu: Salir (para terminar)
```

## Pruebas

Ejecuta la suite de tests:

```bash
pytest test_agent.py -v
```

Con cobertura:

```bash
pytest test_agent.py --cov=tools --cov-report=html
```

## Estructura del Proyecto

```
agent.py          # Agente principal y punto de entrada
tools.py          # Herramientas disponibles para el agente
test_agent.py     # Suite de tests con 40+ casos
conftest.py       # Configuración de pytest
requirements.txt  # Dependencias del proyecto
README.md         # Este archivo
```

## Herramientas Disponibles

- **comparar_instancias_ec2**: Compara características y precios de dos instancias
- **estimar_costo_lambda**: Calcula costo mensual de funciones Lambda
- **recomendar_arquitectura**: Sugiere arquitecturas AWS por caso de uso
- **buscar_servicio_aws**: Lista servicios por categoría (compute, storage, database, ai, networking)
- **calculator**: Realiza operaciones matemáticas
- **current_time**: Obtiene fecha y hora actual