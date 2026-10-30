## 4. Errores, reintentos y escalamiento (lección 4.5)

El asistente utiliza un repertorio explícito de fallos; no completa, sustituye ni ignora evidencia faltante. Ante cualquier paro conserva la traza del caso, declara el motivo y mantiene la salida como borrador. Por tanto, ninguna respuesta a error puede publicar precios, confirmar promociones, modificar acuerdos ni ejecutar acciones comerciales.

### 4.1 Repertorio de respuestas al error

| Tipo de error | Respuesta | Límite de reintentos | Escala a quién y con qué contexto |
|---|---|---:|---|
| Portal ficticio de proveedores sin respuesta | Reintenta con espera creciente de 2, 4 y 8 segundos. Al agotarse el límite, detiene la consulta y no usa una respuesta parcial como evidencia. | 3 | Operaciones recibe el caso preparado, el error citado, la hora del último intento, tienda y producto, así como la traza de los reintentos. |
| Inventario principal ausente, vencido o inconsistente | Detiene la preparación del borrador, pues el inventario es evidencia principal para un posible quiebre. Solicita una captura vigente; no infiere inventario cero a partir de la ausencia de datos. | 0 | Analista Comercial Senior recibe los identificadores del caso, fuente y fecha observada, vigencia requerida, inconsistencia detectada y fuentes que sí permanecen vigentes. Si procede una acción comercial, el caso continúa a revisión del Gerente de Zona. |
| Salida de Luna inválida o incompleta | Rechaza la propuesta si no conserva `tienda_id`, `producto_id`, una acción permitida, las fuentes y la indicación de revisión humana. El sistema conserva el error de validación y genera un borrador local solo cuando existe evidencia suficiente. | 1 nueva solicitud; si falla de nuevo, se detiene | Analista Comercial Senior recibe el mensaje de validación, modalidad y consumo de la llamada, paquete de contexto resumido, fuentes citadas y traza. No se toma el texto inválido como recomendación. |
| Límite de ejecución alcanzado | Detiene el caso al llegar a 12 pasos. No se inician nuevos accesos ni se ejecutan acciones pendientes. | 0 | Analista Comercial Senior recibe la traza completa, último paso exitoso, paso que activó el límite y el borrador, si existe. |
| Evidencias vigentes contradictorias | Reserva la decisión para una persona; el asistente no selecciona una fuente ganadora ni crea una compensación automática. | 0 | Gerente de Zona recibe ambas evidencias con fuente, fecha, vigencia, tienda, producto y la explicación de la contradicción. Si el conflicto afecta un acuerdo del canal moderno, también se solicita revisión jurídica. |

La ejecución del notebook comprobó el primer caso con tres reintentos y el escalamiento a Operaciones. El registro `C3-errores` reportó esperas de 2, 4 y 8 segundos y, después, el estado `escalado_a_operaciones`. Los demás renglones son políticas operativas del diseño: complementan esa demostración sin presentarse como comportamientos ya probados por el notebook.

### 4.2 Política de silla vacía

El estado seguro por defecto es **borrador visible al decisor**. A `t+0 h`, el caso queda en la bandeja con su evidencia, fuentes, vigencias, propuesta y traza, pero no se ejecuta por cuenta propia. Si el responsable no decide antes de `t+4 h`, el sistema genera un recordatorio para el decisor asignado. Si no existe decisión a `t+8 h`, eleva el caso completo a Dirección Comercial y conserva el borrador sin cambios.

La elevación no equivale a una aprobación. El Gerente de Zona, el Área Jurídica cuando corresponda y la Dirección Comercial mantienen sus responsabilidades definidas en el contrato de delegación. En particular, cualquier publicación de precio o promoción sigue requiriendo aprobación humana explícita y auditable.

El notebook verificó esta secuencia mediante tres eventos: caso en bandeja en `t+0 h`, recordatorio en `t+4 h` y elevación a Dirección en `t+8 h`. La simulación no espera horas reales ni envía mensajes; demuestra el orden de la política y que el borrador continúa como estado seguro.

### 4.3 Dos casos obligatorios

**El duplicado.** Antes de crear un borrador, la bandeja compara la combinación de tienda y producto con los casos ya registrados. Si encuentra uno igual, rechaza el segundo registro antes de crear otro borrador y deja constancia en la traza. No ejecuta una acción, reposición ni compensación. En la segunda corrida del notebook, el mismo caso se envió dos veces y el segundo intento fue rechazado como duplicado.

**El conflicto.** Cuando dos evidencias vigentes se contradicen, por ejemplo, una captura de inventario y una observación de campo para la misma tienda y producto, el asistente marca el caso como conflicto y lo reserva para revisión humana. Conserva ambas evidencias, con su fuente, fecha y vigencia, sin combinarlas ni descartar una silenciosamente. En la segunda corrida, el notebook simuló esta condición con `conflicto=True` para un caso distinto del duplicado; el resultado fue la reserva del caso para una persona, no una decisión automática.
