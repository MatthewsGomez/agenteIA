# Design Document: conversation-history

## Overview

Esta feature agrega persistencia del historial de conversación al agente CloudArquitecto.
Se introduce un módulo `history_manager.py` responsable de leer y escribir `historial.json`
en el directorio raíz. El agente carga el historial al arrancar, muestra un resumen y guarda
cada par pregunta/respuesta automáticamente tras cada interacción.

El diseño prioriza:
- Separación de responsabilidades: `agent.py` no manipula JSON directamente.
- Resiliencia: errores de I/O no interrumpen la conversación.
- Formato legible: JSON indentado con campos explícitos.

## Architecture

```mermaid
flowchart TD
    A[agent.py __main__] -->|load_history()| HM[history_manager.py]
    HM -->|lee| F[historial.json]
    A -->|show_summary(entries)| A
    A -->|loop: input()| U[Usuario]
    U --> A
    A -->|agent(user_input)| AG[strands Agent]
    AG -->|respuesta| A
    A -->|save_entry(pregunta, respuesta)| HM
    HM -->|escribe| F
```

El flujo es lineal y síncrono, coherente con el loop `input()` existente en `agent.py`.
No se introducen hilos ni I/O asíncrono.

## Components and Interfaces

### `history_manager.py` (nuevo módulo)

```python
HISTORY_FILE = "historial.json"  # path relativo al directorio raíz

def load_history() -> list[dict]:
    """
    Lee historial.json y retorna la lista de entradas.
    Retorna [] si el archivo no existe o contiene JSON inválido.
    Registra advertencias en stderr según corresponda.
    """

def save_entry(pregunta: str, respuesta: str) -> None:
    """
    Agrega una nueva Conversation_Entry a historial.json.
    Crea el archivo si no existe.
    Registra errores en stderr sin lanzar excepciones.
    """

def format_summary(entries: list[dict]) -> str:
    """
    Retorna un string con el resumen del historial:
    - Si entries está vacío: mensaje de sin conversaciones previas.
    - Si tiene entradas: total de entradas y timestamp de la última.
    """
```

### `agent.py` (modificaciones)

- Importar `load_history`, `save_entry`, `format_summary` desde `history_manager`.
- Al inicio (`__main__`): llamar `load_history()`, imprimir `format_summary(entries)`.
- En el loop: tras obtener la respuesta del agente, llamar `save_entry(user_input, respuesta)`.

La respuesta del agente se captura convirtiendo la llamada `agent(user_input)` para obtener
el string de respuesta antes de imprimirlo (ver Data Models para el tipo de retorno de strands).

## Data Models

### Conversation_Entry

```json
{
  "timestamp": "2024-01-15T10:30:00.123456",
  "pregunta": "¿Cuánto cuesta Lambda con 1M invocaciones?",
  "respuesta": "El costo estimado es..."
}
```

Campos:
- `timestamp`: string ISO 8601 generado con `datetime.utcnow().isoformat()`.
- `pregunta`: string con el input del usuario, sin modificar.
- `respuesta`: string con la respuesta del agente.

### historial.json

```json
[
  {
    "timestamp": "2024-01-15T10:30:00.123456",
    "pregunta": "...",
    "respuesta": "..."
  }
]
```

Arreglo JSON de objetos `Conversation_Entry`, escrito con `json.dump(..., indent=2)`.

### Retorno de `strands Agent`

`agent(user_input)` retorna un objeto `AgentResult`. El texto de la respuesta se obtiene
via `str(result)` o `result.message`. Se usará `str(result)` para máxima compatibilidad.

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system — essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Round-trip de serialización

*For any* lista de `Conversation_Entry` con campos `timestamp`, `pregunta` y `respuesta` válidos,
guardar esa lista en disco y luego cargarla debe producir una lista de objetos equivalente a la original.

**Validates: Requirements 3.3**

---

### Property 2: Acumulación sin pérdida

*For any* secuencia de N entradas guardadas una a una en `historial.json`, la lista cargada
al final debe contener exactamente N entradas en el mismo orden en que fueron guardadas.

**Validates: Requirements 1.2**

---

### Property 3: Estructura y formato del JSON

*For any* `Conversation_Entry` guardada, el archivo `historial.json` resultante debe ser un
arreglo JSON válido donde cada objeto contiene exactamente los campos `timestamp`, `pregunta`
y `respuesta`, y el contenido del archivo usa indentación de 2 espacios.

**Validates: Requirements 3.1, 3.2**

---

### Property 4: Resumen correcto del historial

*For any* lista no vacía de `Conversation_Entry`, el string retornado por `format_summary`
debe contener el número total de entradas y el timestamp de la entrada más reciente (última del arreglo).

**Validates: Requirements 2.4, 4.1, 4.2**

---

### Property 5: Timestamp ISO 8601 en entradas guardadas

*For any* llamada a `save_entry`, la entrada resultante en `historial.json` debe tener un campo
`timestamp` que sea un string parseable como fecha ISO 8601 válida.

**Validates: Requirements 1.1**

---

## Error Handling

| Situación | Comportamiento |
|---|---|
| `historial.json` no existe al cargar | Retornar `[]`, sin mensaje al usuario |
| `historial.json` contiene JSON inválido | Retornar `[]`, advertencia en `stderr` |
| Error de escritura al guardar | Registrar en `stderr`, no lanzar excepción |
| `historial.json` no existe al guardar | Crear el archivo con `[]` y escribir la entrada |

Todos los errores de I/O se capturan con `try/except` en `history_manager.py`.
El agente nunca ve excepciones de persistencia; la conversación continúa siempre.

## Testing Strategy

### Unit Tests (pytest)

Cubren ejemplos concretos y casos borde:

- `test_load_history_file_not_found`: verifica que `load_history()` retorna `[]` cuando el archivo no existe.
- `test_load_history_invalid_json`: verifica que `load_history()` retorna `[]` y escribe en stderr con JSON inválido.
- `test_save_entry_creates_file`: verifica que `save_entry` crea `historial.json` si no existe.
- `test_save_entry_write_error`: mockea `open` para forzar `IOError` y verifica que no se lanza excepción y stderr recibe el error.
- `test_format_summary_empty`: verifica el mensaje para historial vacío.
- `test_agent_startup_calls_load`: verifica (con mock) que al iniciar el agente se llama `load_history`.

### Property-Based Tests (Hypothesis)

Cada propiedad del diseño se implementa como un test con Hypothesis.
Configuración mínima: `@settings(max_examples=100)`.

```python
# Feature: conversation-history, Property 1: Round-trip de serialización
@given(entries=st.lists(conversation_entry_strategy(), min_size=0, max_size=50))
@settings(max_examples=100)
def test_round_trip(tmp_path, entries): ...

# Feature: conversation-history, Property 2: Acumulación sin pérdida
@given(entries=st.lists(conversation_entry_strategy(), min_size=1, max_size=30))
@settings(max_examples=100)
def test_accumulation(tmp_path, entries): ...

# Feature: conversation-history, Property 3: Estructura y formato del JSON
@given(entry=conversation_entry_strategy())
@settings(max_examples=100)
def test_json_structure_and_format(tmp_path, entry): ...

# Feature: conversation-history, Property 4: Resumen correcto del historial
@given(entries=st.lists(conversation_entry_strategy(), min_size=1, max_size=50))
@settings(max_examples=100)
def test_summary_content(entries): ...

# Feature: conversation-history, Property 5: Timestamp ISO 8601
@given(entry=conversation_entry_strategy())
@settings(max_examples=100)
def test_timestamp_iso8601(tmp_path, entry): ...
```

La estrategia `conversation_entry_strategy()` genera dicts con `pregunta` y `respuesta`
como strings arbitrarios (incluyendo unicode y caracteres especiales).

Librería: **Hypothesis** (`pip install hypothesis`), compatible con pytest y el entorno Python existente.
