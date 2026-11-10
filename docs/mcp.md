# MCP: propuesta de una interfaz acotada

**Estado: diseño, no servidor implementado ni publicado.**

MCP permite exponer herramientas a un asistente. Una primera integración de esta torre debería ofrecer únicamente:

- `observe_capacity`: devolver bytes, momento y método, sin rutas personales, procesos o documentos.
- `explain_admission`: calcular un escenario a partir de una observación explícita, una reserva y una demanda declarada; devolver motivo y caducidad, nunca un permiso de ejecución.

La interfaz debería comenzar por transporte local stdio y validación estricta. No necesita credenciales ni un endpoint público. Los metadatos `readOnlyHint`, `destructiveHint` y `openWorldHint` describen el alcance para el cliente; no reemplazan los controles del servidor. Véase la [explicación oficial de las anotaciones](https://blog.modelcontextprotocol.io/posts/2026-03-16-tool-annotations/).

Un servidor que ejecute inferencias requiere otro contrato: identidad del operador, exclusión verificable, límites de tiempo, cancelación de procesos descendientes, presupuesto, restauración y pruebas con el runtime concreto. No conviene conceder esa autoridad a partir de una respuesta favorable de `explain_admission`.

Antes de implementar: fijar la versión de protocolo soportada y el SDK oficial, probar inicialización, esquemas inválidos, errores, salida incompleta y desconexión; revisar la [especificación oficial](https://github.com/modelcontextprotocol/modelcontextprotocol/tree/main/docs/specification). Este documento no acredita compatibilidad con clientes MCP.
