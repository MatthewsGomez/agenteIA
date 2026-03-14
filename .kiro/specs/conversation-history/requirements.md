# Requirements Document

## Introduction

Esta feature agrega persistencia del historial de conversación al agente CloudArquitecto.
Cada interacción (pregunta del usuario y respuesta del agente) se guarda en `historial.json`
con un timestamp. Al iniciar, el agente carga el historial existente y muestra un resumen.

## Glossary

- **Agent**: El agente CloudArquitecto definido en `agent.py`.
- **History_Manager**: Módulo responsable de leer y escribir el historial en disco.
- **Conversation_Entry**: Una entrada del historial compuesta por timestamp, pregunta y respuesta.
- **historial.json**: Archivo JSON en el directorio raíz del proyecto donde se persiste el historial.
- **Summary**: Representación condensada del historial que muestra las últimas entradas al inicio.

## Requirements

### Requirement 1: Persistencia de entradas de conversación

**User Story:** Como usuario de CloudArquitecto, quiero que cada pregunta y respuesta se guarde automáticamente, para poder revisar conversaciones anteriores.

#### Acceptance Criteria

1. WHEN el usuario envía una pregunta y el agente genera una respuesta, THE History_Manager SHALL guardar una Conversation_Entry en historial.json con timestamp ISO 8601, la pregunta y la respuesta.
2. THE History_Manager SHALL agregar cada nueva Conversation_Entry al arreglo existente en historial.json sin sobrescribir entradas previas.
3. IF historial.json no existe al intentar guardar, THEN THE History_Manager SHALL crear el archivo con un arreglo JSON válido antes de escribir la entrada.
4. IF ocurre un error de escritura en historial.json, THEN THE History_Manager SHALL registrar el error en stderr y continuar la ejecución del Agent sin interrumpir la conversación.

### Requirement 2: Carga del historial al inicio

**User Story:** Como usuario de CloudArquitecto, quiero que el agente cargue el historial previo al iniciar, para tener contexto de conversaciones anteriores disponible desde el arranque.

#### Acceptance Criteria

1. WHEN el Agent inicia, THE History_Manager SHALL intentar leer historial.json desde el directorio raíz del proyecto.
2. IF historial.json no existe al iniciar, THEN THE History_Manager SHALL inicializar un historial vacío sin mostrar error al usuario.
3. IF historial.json contiene JSON inválido, THEN THE History_Manager SHALL inicializar un historial vacío y registrar una advertencia en stderr.
4. WHEN el historial cargado contiene al menos una Conversation_Entry, THE Agent SHALL mostrar un resumen con el número total de entradas y la fecha de la última conversación antes de iniciar el loop de input.
5. WHEN el historial cargado está vacío, THE Agent SHALL mostrar un mensaje indicando que no hay conversaciones previas.

### Requirement 3: Formato del archivo historial.json

**User Story:** Como desarrollador, quiero que historial.json tenga un formato estructurado y legible, para poder inspeccionarlo o procesarlo con otras herramientas.

#### Acceptance Criteria

1. THE History_Manager SHALL estructurar historial.json como un arreglo JSON de objetos, donde cada objeto contiene exactamente los campos: `timestamp` (string ISO 8601), `pregunta` (string) y `respuesta` (string).
2. THE History_Manager SHALL escribir historial.json con indentación de 2 espacios para facilitar la lectura humana.
3. FOR ALL Conversation_Entry escritas y luego leídas, THE History_Manager SHALL producir objetos equivalentes al original (propiedad round-trip).

### Requirement 4: Resumen del historial

**User Story:** Como usuario de CloudArquitecto, quiero ver un resumen conciso del historial al iniciar, para saber rápidamente cuántas conversaciones previas existen y cuándo fue la última.

#### Acceptance Criteria

1. WHEN el Agent muestra el resumen del historial, THE Agent SHALL incluir el número total de Conversation_Entry almacenadas.
2. WHEN el Agent muestra el resumen del historial, THE Agent SHALL incluir el timestamp de la Conversation_Entry más reciente formateado de forma legible.
3. THE Agent SHALL mostrar el resumen del historial antes del primer prompt de input al usuario.
