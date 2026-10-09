# Especificación y primer agente funcional

**Construye 2 · Diseño e implementación de sistemas agénticos · Tecnológico de Monterrey**

| Equipo | Conjunto de datos | Fecha |
|---|---|---|
| Equipo 24 | Distribuidora Cuauhtémoc (común) | 8 de octubre de 2026 |

## 1. Especificación de comportamiento (lección 3.2)

### 1.1 Objetivo operacionalizado

Esta especificación acota el objetivo delegado a la detección y priorización de **señales de quiebre potencial**. No confirma un quiebre real, porque los datos no incluyen planogramas ni el catálogo esperado por tienda; tampoco propone precios ni promociones. Esas decisiones permanecen dentro del contrato de delegación y se reservan para etapas posteriores.

En cada corrida, el agente busca combinaciones tienda-producto con al menos 2 fechas de `unidades_disponibles = 0` en los 7 días calendario, inclusivos, que terminan en la fecha de corte del inventario diario. Dos observaciones reducen el riesgo de reaccionar a un ajuste aislado; la regla se aplica al dataset sintético diario y deberá ajustarse antes de usarla en canales cuya captura real sea semanal o quincenal.

La clasificación sigue este orden obligatorio y un caso conserva solo el primer estado que le corresponda:

1. `EVIDENCIA_INSUFICIENTE`: faltan identificadores, fecha válida, `precio_lista`, `costo` o `rotacion_esperada`. Genera una alerta al analista con la brecha; no crea borrador.
2. `DESFASE_O_INCONSISTENCIA`: existe inventario cero y ventas positivas para la misma tienda-producto-fecha. Puede ser un desfase de captura o una inconsistencia; registra ambos valores y solicita revisión de la fuente, sin crear borrador.
3. `ESCALAMIENTO`: existe una promoción activa para el mismo producto, zona y canal en la fecha de corte. Empaqueta la evidencia para revisión humana, sin crear borrador.
4. `POSIBLE_QUIEBRE`: cumple la señal de dos ceros y no cae en los estados anteriores.
5. `PRIORIZADO`: es un posible quiebre con evidencia completa. Se ordena junto con los demás casos válidos por margen potencial en riesgo dentro de cada combinación de `categoria` y `canal`.

El margen potencial en riesgo se estima como $días\ en\ cero \times (rotación\ esperada/7) \times (precio\ de\ lista - costo)$, usando `rotacion_esperada`, `precio_lista` y `costo` del maestro de productos. El cálculo establece orden relativo, no un umbral monetario ni una decisión automática. Para un caso `PRIORIZADO`, el agente genera exclusivamente un borrador de reposición urgente para aprobación humana del gerente con `tienda_id`, `producto_id`, fecha de corte, evidencia, impacto y posición de prioridad; no comunica ni ejecuta ninguna acción comercial. Esto operacionaliza el objetivo delegado y el margen de decisión establecidos en las secciones 1 y 2 del contrato de delegación.

Para evaluar una promoción activa, el agente obtiene `zona` y `canal` del maestro de tiendas mediante `tienda_id` y busca en el calendario promocional una fila con el mismo `producto_id`, zona y canal, `estado = activa` y `fecha_inicio <= fecha_corte <= fecha_fin`.

### 1.2 Entradas y vigencia

La corrida fija una fecha de corte común para comparar fuentes, pero evalúa la frescura de cada una según su frecuencia operativa. Una fuente puede ser válida para describir el historial y, al mismo tiempo, no ser suficientemente reciente para sostener una propuesta.

| Fuente | Ventana de vigencia | Qué pasa cuando caduca a media corrida |
|---|---|---|
| Ventas facturadas del ERP | Actualización diaria; la fecha máxima de `fecha` debe coincidir con la fecha de corte o ser del día inmediato anterior. El historial de 28 días anteriores se usa solo para contexto de demanda. | Si llega una actualización durante la corrida, conserva el corte inicial y reinicia el análisis antes de emitir una propuesta. |
| Inventario del canal moderno | Actualización diaria por tienda; la fecha máxima de inventario debe coincidir con la fecha de corte o ser del día inmediato anterior. Los 7 días calendario previos se usan para detectar ceros repetidos. | Si el inventario no está actualizado, el caso se registra como `EVIDENCIA_INSUFICIENTE`; no crea borrador. |
| Inventario capturado en campo del canal tradicional | Actualización por visita. Es vigente hasta la siguiente visita programada: máximo 7 días para tienda semanal y 14 para tienda quincenal, según su frecuencia registrada. | Si se supera la frecuencia esperada, se declara captura vencida, se pide revisión o nueva visita y no se crea borrador con esa señal. |
| Capturas de precios de competencia | Actualización por visita. Usan la misma vigencia de la tienda: máximo 7 días para visita semanal y 14 para quincenal. | Si la captura vence, se declara como contexto no vigente; se solicita una nueva captura o se escala al gerente, sin recomendar cambios de precio. |
| Calendario promocional | Vigente cuando la fecha de corte está entre inicio y fin de una promoción con estado activo. | Si se modifica durante la corrida, se reinicia la validación de conflicto antes de emitir propuesta. |
| Maestro de productos, precios y costos | Debe ser la versión consultada en la corrida; sus campos de producto, costo, precio y rotación se registran con la fecha de corte. | Si falta un atributo necesario o no se puede asociar con el corte, el caso recibe `EVIDENCIA_INSUFICIENTE`. |

### 1.3 Restricciones

1. Solo se permiten los borradores `reposicion urgente (aprueba gerente)`, `ajuste de pedido sugerido` y `alerta a preventista`; una acción fuera del catálogo se bloquea antes de la bandeja. Corresponde al margen de decisión y al poder de escritura del contrato, sección 2 y 3.
2. No se comunica un precio, promoción o pedido al mercado ni se modifica un acuerdo comercial; el prototipo solo guarda borradores reversibles. Corresponde a las prohibiciones del contrato, sección 2, y a las acciones irreversibles de la sección 4.
3. Las validaciones ocurren antes de escribir: primero, se comprueba que los maestros y atributos requeridos existan; después, se valida cada candidato y se asigna el primer estado aplicable; por último, solo un caso `PRIORIZADO` puede comprobar de nuevo sus identificadores, fecha ISO, impacto calculado y acción permitida. Un fallo de estructura bloquea la corrida; un fallo de candidato genera `EVIDENCIA_INSUFICIENTE`. Corresponde al registro auditable exigido en las secciones 3, 4 y 5 del contrato.
4. Los datos por tienda del canal moderno permanecen dentro de la infraestructura autorizada; el agente no exporta datos ni usa correo. Corresponde a la prohibición de exposición y al límite de acceso del contrato, secciones 2 y 3.
5. Un caso `EVIDENCIA_INSUFICIENTE`, `DESFASE_O_INCONSISTENCIA` o `ESCALAMIENTO` no puede crear un borrador de reposición: el primero solicita completar la evidencia, el segundo solicita revisión de la fuente y el tercero empaqueta evidencia para revisión humana. Corresponde a la obligación de validar fuente, vigencia y consistencia antes de recomendar, del contrato, sección 4.

### 1.4 Criterios de éxito

| Criterio | Cómo se verifica en el caso preparado |
|---|---|
| Señal de quiebre potencial | Hay al menos 2 fechas con `unidades_disponibles = 0` en los 7 días calendario hasta la fecha de corte. |
| Precedencia de estados | Cada candidato recibe exactamente un estado según el orden declarado en 1.1; los estados que bloquean borrador se registran con su evidencia. |
| Consistencia de fuente | Si una fecha compartida tiene `unidades_disponibles = 0` y `ventas.unidades > 0` para la misma tienda-producto, se registra `DESFASE_O_INCONSISTENCIA`, no una afirmación de error confirmado. |
| Sin conflicto comercial | Una promoción activa se verifica con producto, zona, canal y rango de fechas; si coincide, el estado es `ESCALAMIENTO`. |
| Evidencia identificable y fechada | `tienda_id` y `producto_id` son no vacíos, existen en los maestros de tiendas y productos, y `fecha_corte` usa el formato ISO `YYYY-MM-DD`. |
| Acción dentro del contrato | La propuesta pertenece al catálogo de tres acciones permitidas y no contiene precio, promoción ni modificación de acuerdo comercial. |
| Escritura segura y trazable | Antes de guardar el borrador se validan identificadores, fecha, impacto calculado y acción; el registro conserva fuentes, fecha de corte, evidencia, propuesta y responsable de aprobación. |

Cada registro de traza contiene `fase`, `fecha_hora`, `estado`, `tienda_id`, `producto_id`, fuentes y cortes usados, evidencia, propuesta o motivo de no propuesta, y responsable de aprobación cuando aplique. Los hallazgos de una misma fase pueden resumirse con conteos y referencias a los candidatos; siempre debe existir un registro de cierre.

### 1.5 Condiciones de paro: las cuatro familias

Para cada candidato, el agente dispone de hasta **12 verificaciones unitarias**. Las primeras 11 son necesarias para llegar a una conclusión: (1) `tienda_id` presente, (2) `producto_id` presente, (3) tienda existente en su maestro, (4) producto existente en su maestro, (5) fecha de corte válida, (6) inventario vigente, (7) ventas vigentes, (8) dos fechas de inventario cero en la ventana, (9) cruce de ventas en la misma fecha, (10) conflicto con promoción activa y (11) atributos de margen y acción permitida antes de escribir. La verificación 12 queda reservada para repetir exactamente una comprobación si una fuente cambió durante la corrida o si se detectó una discrepancia. No limita registros de traza ni candidatos: cada candidato conserva su propio presupuesto y todas sus comprobaciones quedan registradas.

| Familia | Condición con su valor | Qué hace el agente |
|---|---|---|
| Éxito | Un `POSIBLE_QUIEBRE` completa las 11 verificaciones obligatorias, se ordena como `PRIORIZADO` y se guarda un borrador con estado final registrado. | Registra `ÉXITO`, conserva el borrador reversible y deja la aprobación al gerente. |
| Límite | Se agotaron las 12 verificaciones de un candidato y aún no hay una conclusión; la comprobación adicional ya se usó para revalidar una fuente o discrepancia. | No crea borrador para ese candidato, registra `PARO POR LÍMITE` y escala al analista con las verificaciones realizadas, la fuente pendiente y el motivo. |
| Imposibilidad | Ninguna combinación tienda-producto alcanza dos fechas en cero en 7 días. | Registra `IMPOSIBILIDAD`, no inventa un candidato ni escribe un borrador. Los casos con una sola fecha en cero se registran como `ALERTA_DEBIL` para seguimiento humano. |
| Escalamiento | El producto candidato coincide con una promoción activa para su zona y canal, o la evidencia competitiva vigente no basta para recomendar. | Empaqueta evidencia y registra `ESCALAMIENTO` para revisión humana, sin notificar ni escribir un borrador. |

### 1.6 Manejo de incertidumbre

El agente declara la antigüedad de cada fuente en la traza. Las capturas de precios de competencia con más de 10 días no sostienen una recomendación de precio: se reportan como caducas y se pide una nueva captura a preventa o se escala al gerente. Si falta evidencia fechada, la verificación asigna `EVIDENCIA_INSUFICIENTE` antes de guardar el borrador. Si una fecha tiene inventario cero y ventas positivas para la misma tienda-producto, el agente asigna `DESFASE_O_INCONSISTENCIA` y solicita revisión de la fuente. Si existe una promoción activa del mismo `producto_id`, zona y canal, prepara el paquete de conflicto y escala; no infiere que la promoción sea válida ni recomienda cambiarla. Los datos de competencia se usan aquí solo para declarar su vigencia, porque no incluyen una clave explícita que relacione `producto_competidor_id` con el `producto_id` interno.

## 2. Cinco decisiones de arquitectura (lección 3.5)

| Decisión | Su elección | Alternativa descartada y por qué |
|---|---|---|
| Alcance de la etapa | Detectar y clasificar posibles quiebres, inconsistencias y conflictos; crear solo borradores de reposición para casos priorizados y escalar conflictos. | Automatizar promociones o precios. Se descarta porque requeriría aprobación humana, reglas comerciales y, en canal moderno, revisión jurídica; ejecutarlo violaría el contrato. |
| Estructura del estado | Caso estructurado con tienda, producto, zona, canal, impacto de margen, posición de prioridad, fecha de corte, acción, conflicto y evidencia; estado separado entre la traza y el borrador. | Texto libre de recomendación. Se descarta porque no permite validar campos, auditar evidencia ni bloquear acciones no permitidas. |
| Catálogo de herramientas | Lectura de las siete fuentes, detector de quiebres sobre inventario diario, cruce de inventario y ventas facturadas, consulta de promociones por producto-zona-canal, cálculo de vigencia, verificador determinista y registro de borradores. | Acceso a correo, ERP de escritura o acuerdos editables. Se descarta porque el contrato niega esos permisos y convertiría una prueba en una acción irreversible. |
| Dónde verificar | Antes de guardar el borrador: identificadores presentes en los catálogos, fecha, impacto calculado y acción permitida; el registro vuelve a validar la existencia de tienda y producto. | Verificar después de crear el borrador. Se descarta porque una propuesta inválida ya habría entrado al registro operativo y perdería el control preventivo. |
| Traza para dos lectores | Registros de fase, detalle y evidencia; salida resumida para el gerente y campos reproducibles para analista/auditor. | Solo un resultado final. Se descarta porque no permitiría reconstruir fuente, vigencia, impacto, prioridad, conflicto ni motivo de paro. |

## 3. Evidencia de ejecución

**Evidencias de ejecución en el PDF:**

Pendiente de incorporar. La evidencia deberá mostrar la fecha de corte de cada fuente, los parámetros aplicados, los candidatos detectados, las validaciones previas al borrador y el estado final de cada corrida. No se reportan resultados hasta ejecutar el agente sobre el conjunto de datos.

**Ejecución 1 — caso completo: criterios comprobados y estado final obtenido:**

Pendiente de ejecución. Documentar el número de combinaciones con al menos dos fechas de inventario cero en la ventana de siete días, los casos marcados como `INCONSISTENCIA`, el candidato priorizado, su evidencia, el resultado de las validaciones y el estado final del borrador.

**Ejecución 2 — resultado de escalamiento con su paquete:**

Pendiente de ejecución. Documentar un candidato cuyo `producto_id` tenga una promoción activa en su zona y canal, el paquete de evidencia del calendario promocional y el estado `ESCALAMIENTO`, sin crear ni comunicar una acción comercial.

**Ejecución 2 — resultado de imposibilidad declarada:**

Pendiente de ejecución. Usar una condición que ningún candidato satisfaga, registrar `IMPOSIBILIDAD` sin crear propuesta y documentar por separado un `PARO POR LÍMITE` al agotar las 12 verificaciones de un candidato sin lograr una conclusión.

## Autoevaluación contra la rúbrica

| Criterio | Peso (%) | Dónde está nuestra evidencia |
|---|---:|---|
| Especificación verificable y completa (seis piezas, cuatro familias de paro) | 30 | Secciones 1.1 a 1.6; los predicados se aplican a los campos de los CSV identificados en cada sección. |
| Coherencia con el contrato de delegación (trazabilidad doble) | 25 | Secciones 1.1 y 1.3; contrato de delegación, secciones 2 a 5. La evidencia de bloqueo se agregará tras la ejecución. |
| Decisiones de arquitectura justificadas con alternativa descartada | 20 | Sección 2. |
| Evidencia de ejecución con traza legible para dos lectores | 15 | Pendiente de ejecutar y anexar en la sección 3. |
| Manejo de incertidumbre y escalamiento demostrado | 10 | Secciones 1.2 y 1.6; pendiente de demostrar con la corrida documentada. |

## Apéndices (obligatorios, no puntuados)

### A. Contribución del equipo

| Sección | Responsable | La decisión más discutida |
|---|---|---|
| 1.1 Objetivo operacionalizado y 1.2 Entradas y vigencia | Carlos Alcántar | Usar vigencias distintas para ventas, inventarios y competencia sin confundirlas con la ventana de detección. |
| 1.3 Restricciones, 1.4 Criterios de éxito y 1.5 Condiciones de paro | Rodrigo Robledo | Verificar antes de escribir y registrar la imposibilidad o el límite en lugar de fabricar un caso. |
| 1.6 Manejo de incertidumbre y sección 2 de arquitectura | David Hernández | Escalar evidencia competitiva caduca o conflictos de promociones sin convertirlos en una acción comercial. |
| Sección 3, autoevaluación y revisión final | Cesar Avila | Distinguir el borrador reversible del simulador de una autorización o comunicación externa. |

### B. Declaración de uso de IA

La IA está permitida, no es obligatoria. Declara su uso; si no la utilizaron, indícalo. El equipo es responsable de verificar su trabajo.

**Qué le delegamos:** se utilizó ChatGPT y GitHub Copilot para estructurar el borrador de la especificación a partir del contrato de delegación, el caso estándar y el esquema de las fuentes de datos.

**Qué verificamos:** se contrastaron los atributos usados (`fecha`, identificadores, unidades disponibles, precios, rotación, promociones y capturas) contra las fuentes de datos, y las acciones permitidas, estados de paro y restricciones contra las secciones 2 a 5 del contrato de delegación.

**Qué corregimos:** se eliminó cualquier afirmación de ejecución no sustentada por los CSV. También se corrigió la redacción para no afirmar que el agente envía pedidos, publica precios o ejecuta promociones. Las evidencias de ejecución permanecen pendientes hasta contar con trazas reales.

*Si falta un apéndice, consulta al equipo docente. Cualquier ampliación del plazo requiere autorización expresa conforme a las Políticas del curso.*
