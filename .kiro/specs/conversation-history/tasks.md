# Implementation Plan: conversation-history

## Overview

Implementar persistencia del historial de conversación en CloudArquitecto creando `history_manager.py`
y modificando `agent.py` para cargar, mostrar y guardar entradas en `historial.json`.

## Tasks

- [x] 1. Crear `history_manager.py` con las funciones base
  - Crear el archivo `history_manager.py` en el directorio raíz
  - Definir la constante `HISTORY_FILE = "historial.json"`
  - Implementar `load_history() -> list[dict]`: leer `historial.json`, retornar `[]` si no existe o JSON inválido, registrar advertencia en stderr en caso de JSON inválido
  - Implementar `save_entry(pregunta: str, respuesta: str) -> None`: construir una `Conversation_Entry` con `timestamp` ISO 8601 via `datetime.utcnow().isoformat()`, cargar el arreglo existente (o `[]` si no existe), agregar la nueva entrada y escribir con `json.dump(..., indent=2)`; capturar errores de I/O y registrarlos en stderr sin lanzar excepción
  - Implementar `format_summary(entries: list[dict]) -> str`: retornar mensaje de sin conversaciones previas si vacío, o total de entradas + timestamp de la última entrada formateado de forma legible si no vacío
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 3.1, 3.2, 4.1, 4.2_

  - [ ]* 1.1 Escribir tests unitarios para `history_manager.py`
    - `test_load_history_file_not_found`: verifica retorno `[]` cuando el archivo no existe
    - `test_load_history_invalid_json`: verifica retorno `[]` y escritura en stderr con JSON inválido
    - `test_save_entry_creates_file`: verifica que `save_entry` crea `historial.json` si no existe
    - `test_save_entry_appends_without_overwrite`: verifica que entradas previas no se sobrescriben al agregar una nueva
    - `test_save_entry_write_error`: mockea `open` para forzar `IOError`, verifica que no se lanza excepción y stderr recibe el error
    - `test_format_summary_empty`: verifica mensaje para historial vacío
    - `test_format_summary_non_empty`: verifica que el resumen incluye total de entradas y timestamp de la última
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.2, 2.3, 4.1, 4.2_

  - [ ]* 1.2 Escribir property test — Property 1: Round-trip de serialización
    - **Property 1: Round-trip de serialización**
    - Para cualquier lista de `Conversation_Entry` válidas, guardar cada entrada con `save_entry` y luego llamar `load_history` debe producir una lista equivalente a la original
    - Usar `@given(entries=st.lists(conversation_entry_strategy(), min_size=0, max_size=50))`
    - **Validates: Requirements 3.3**

  - [ ]* 1.3 Escribir property test — Property 2: Acumulación sin pérdida
    - **Property 2: Acumulación sin pérdida**
    - Para cualquier secuencia de N entradas guardadas una a una con `save_entry`, la lista retornada por `load_history` al final debe contener exactamente N entradas en el mismo orden
    - Usar `@given(entries=st.lists(conversation_entry_strategy(), min_size=1, max_size=30))`
    - **Validates: Requirements 1.2**

  - [ ]* 1.4 Escribir property test — Property 3: Estructura y formato del JSON
    - **Property 3: Estructura y formato del JSON**
    - Para cualquier `Conversation_Entry` guardada con `save_entry`, el archivo resultante debe ser un arreglo JSON válido donde cada objeto contiene exactamente los campos `timestamp`, `pregunta` y `respuesta`, y el contenido usa indentación de 2 espacios
    - Usar `@given(entry=conversation_entry_strategy())`
    - **Validates: Requirements 3.1, 3.2**

  - [ ]* 1.5 Escribir property test — Property 4: Resumen correcto del historial
    - **Property 4: Resumen correcto del historial**
    - Para cualquier lista no vacía de `Conversation_Entry`, `format_summary` debe retornar un string que contenga el número total de entradas y el timestamp de la última entrada
    - Usar `@given(entries=st.lists(conversation_entry_strategy(), min_size=1, max_size=50))`
    - **Validates: Requirements 2.4, 4.1, 4.2**

  - [ ]* 1.6 Escribir property test — Property 5: Timestamp ISO 8601
    - **Property 5: Timestamp ISO 8601 en entradas guardadas**
    - Para cualquier llamada a `save_entry`, la entrada resultante en `historial.json` debe tener un campo `timestamp` parseable como fecha ISO 8601 válida via `datetime.fromisoformat`
    - Usar `@given(entry=conversation_entry_strategy())`
    - **Validates: Requirements 1.1**

- [ ] 2. Checkpoint — Verificar que todos los tests de `history_manager.py` pasan
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 3. Modificar `agent.py` para integrar el historial
  - Agregar imports: `from history_manager import load_history, save_entry, format_summary`
  - En el bloque `__main__`, antes del loop: llamar `entries = load_history()` e imprimir `format_summary(entries)`
  - En el loop, reemplazar la llamada directa `agent(user_input)` por: `result = agent(user_input)` para capturar el resultado, luego llamar `save_entry(user_input, str(result))`; el agente ya imprime la respuesta internamente, por lo que no se debe imprimir `result` por separado
  - _Requirements: 2.1, 2.4, 2.5_

  - [ ]* 3.1 Escribir test de integración para el arranque del agente
    - `test_agent_startup_calls_load`: verifica con mock que al iniciar el agente se llama `load_history` y se imprime el resultado de `format_summary`
    - `test_agent_startup_empty_history`: verifica que el mensaje de sin conversaciones previas se muestra cuando el historial está vacío
    - _Requirements: 2.1, 2.4, 2.5_

- [ ] 4. Checkpoint final — Verificar integración completa
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Las sub-tareas marcadas con `*` son opcionales y pueden omitirse para un MVP más rápido
- La estrategia `conversation_entry_strategy()` debe generar dicts con `pregunta` y `respuesta` como strings arbitrarios (incluyendo unicode y caracteres especiales)
- Todos los property tests usan `@settings(max_examples=100)` de Hypothesis
- `save_entry` nunca lanza excepciones; los errores de I/O van a stderr
- El archivo `historial.json` se escribe con `json.dump(..., indent=2)`
- `agent(user_input)` de strands imprime la respuesta internamente; `str(result)` se usa solo para persistir en el historial
