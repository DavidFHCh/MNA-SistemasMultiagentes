# Contrato de delegación

**Construye 1 · Diseño e implementación de sistemas agénticos · Tecnológico de Monterrey**

| Equipo | Variante del dataset | Fecha |
|---|---|---|
| Equipo 24 | v03 | 22 de septiembre de 2026 |

## Caso

Distribuidora Cuauhtémoc es una empresa mexicana de consumo masivo con dos categorías: alimentos empacados y cuidado personal. Opera una planta, seis centros de distribución regionales y una fuerza de ventas de 340 preventistas. Factura alrededor de 4,800 millones de pesos anuales. Sus marcas compiten contra dos multinacionales y una creciente marca propia de los autoservicios.

Vende por cuatro canales:

- **Canal moderno (34 % de la venta):** autoservicios nacionales que operan con pedidos electrónicos y acuerdos comerciales trimestrales.
- **Mayoreo (18 %):** surte a distribuidores secundarios.
- **Cadenas de conveniencia (16 %):** exigen cumplimiento estricto de planograma y tienen penalizaciones por quiebre.
- **Canal tradicional (32 %):** 41,000 tiendas de barrio atendidas por preventistas con visita semanal o quincenal. Es el canal con mayor margen y el más difícil de observar: la única señal confiable es lo que la preventista captura en su terminal durante la visita.

Este caso consiste en generar un sistema agéntico de inteligencia comercial que ayude a detectar anomalías, investigar causas probables y proponer acciones concretas gracias a la observación de datos de ventas, inventario y competencia.

## 1. Objetivo delegado (15 pts)

Identificar señales de venta, inventario y competencia que soporten decisiones sobre quiebres de anaquel, comportamientos comerciales o cambios de precio de la competencia, y determinar acciones por tienda, zona o canal sustentadas en evidencia objetiva que permita la toma final de decisión por parte de un ser humano.

El sistema debe procesar la información disponible para reducir el tiempo de detección del análisis manual, lograr una alerta en menos de 24 horas y asegurar, mediante un proceso auditable, que en el 100 % de los casos sea un ser humano quien tome la decisión final.

## 2. Margen de decisión (30 pts)

### Decide solo

El agente podrá:

1. Identificar señales comerciales asociadas con posibles quiebres de anaquel.
2. Analizar inventarios, promociones vigentes y precios de la competencia para identificar anomalías y generar hipótesis sobre el estado actual y sus causas probables.
3. Crear alertas cuando la evidencia disponible sea insuficiente para generar propuestas.
4. Generar vistas, alertas y reportes que apoyen la toma de decisiones gerenciales o jurídicas.

### Propone y espera aprobación

El agente deberá proponer:

1. Promociones por tienda, zona o canal que cumplan con las reglas comerciales.
2. Ajustes a precios promocionales de acuerdo con los datos históricos y capturados.
3. Propuestas para el área jurídica sobre el canal moderno (autoservicios nacionales), con base en los acuerdos comerciales trimestrales.
4. Acciones ante posibles quiebres de anaquel, como priorizar la atención o recomendar reposición.
5. Acciones comerciales ante cambios relevantes en los precios de la competencia.

### Tiene prohibido decidir

El agente no podrá:

1. Comunicar precios o promociones al mercado hasta que exista una aprobación humana explícita y auditable.
2. Modificar acuerdos comerciales sin que el área jurídica haya realizado una revisión y aprobación auditable.
3. Exponer información fuera de la infraestructura autorizada; deberá proteger la confidencialidad de la información y de los convenios comerciales previos y vigentes.
4. Ignorar restricciones comerciales vigentes, ya que incumplirlas puede generar sanciones contractuales.

## 3. Poder otorgado (20 pts)

El agente deberá contar con atribuciones y restricciones bajo las siguientes premisas:

- **Lectura:** acceso a Sistemas de Preventa, ERP, Convenios Comerciales, Precios de productos, Inventarios y Propuestas.
- **Escritura:** generación de alertas, recomendaciones y registros auditables (evidencias, razonamientos, propuesta, responsable de aprobación y decisión humana).
- **Sin acceso a:** correos corporativos para envío de propuestas, modificaciones de acuerdos comerciales o cambios de precios.

## 4. Acciones irreversibles (20 pts)

| Acción | Mecanismo de protección |
|---|---|
| Publicación o comunicación de un precio o promoción al mercado | Aprobación obligatoria del gerente de zona o responsable comercial y, cuando aplique, revisión del área jurídica. |
| Confirmación de una promoción del canal moderno que coincida con acuerdos comerciales trimestrales | Validación obligatoria del área jurídica antes de su aprobación y ejecución. |
| Ejecución de una acción comercial basada en información incorrecta, incompleta o desactualizada | Validar la fuente, vigencia y consistencia de la información; cuando la evidencia sea insuficiente, solicitar información adicional a preventa antes de emitir la recomendación. |
| Modificación o comunicación de precios promocionales | Validación determinista de las reglas comerciales para todas las propuestas generadas y aprobación humana antes de su ejecución. |
| Exposición de información confidencial fuera de la infraestructura autorizada | Controles tecnológicos de acceso, restricción de exportación y procesamiento exclusivo dentro de la infraestructura autorizada. |
| Ejecución de acciones sin trazabilidad | Toda recomendación y aprobación deberá registrar evidencia, razonamiento, propuesta, responsable, fecha y decisión final. |

## 5. Responsabilidad y Model Decision Card (15 pts)

### Responsabilidades

| Acción | Responsable | Ante quién responde | Registro exigible |
|---|---|---|---|
| Captura de información de inventario, precios de competencia y visita en campo | Preventista | Gerente de Zona | Preventista, tienda, fecha y hora de visita, información capturada y origen de los datos. |
| Operación del asistente y revisión de alertas, análisis y recomendaciones | Analista Comercial Senior | Dirección Comercial | Fuentes consultadas, vigencia de los datos, señales detectadas, hipótesis consideradas y recomendación generada. |
| Aprobación de promociones y acciones comerciales por tienda, zona o canal | Gerente de Zona | Director Comercial | Propuesta recibida, reglas comerciales validadas, decisión tomada, fecha y responsable de aprobación. |
| Revisión de promociones del canal moderno relacionadas con acuerdos comerciales trimestrales | Área Jurídica | Dirección Comercial | Promoción propuesta, acuerdo comercial relacionado, revisión jurídica y resultado de la validación. |
| Custodia y protección de información confidencial del canal moderno | Área de Datos | Dirección Comercial | Fuente de los datos, usuarios o sistemas que accedieron, fecha de acceso y evidencia de que el procesamiento ocurrió dentro de la infraestructura autorizada. |
| Autorización final de decisiones comerciales de mayor impacto | Director Comercial | Dirección de la empresa | Recomendación recibida, evidencia utilizada, decisión final y justificación correspondiente. |

### Model Decision Card

| Tarea principal | Perfil del modelo | Justificación |
|---|---|---|
| Clasificación y priorización de señales comerciales, como posibles quiebres de anaquel, cambios relevantes de inventario o movimientos de la competencia. | Modelo rápido | Existe un volumen elevado de señales que deben procesarse con baja latencia. Un error de clasificación es relativamente barato y reversible porque la alerta será revisada antes de ejecutar una acción comercial. |
| Investigación de causas probables y generación de recomendaciones. | Modelo capaz | La tarea requiere relacionar información de ventas, inventarios, promociones, visitas y precios de competencia, distinguir evidencia de hipótesis y producir una recomendación que será utilizada por gerentes o el área jurídica para apoyar decisiones de mayor impacto. |
| Validación de reglas comerciales de promociones y precios. | Sin modelo | Las reglas son deterministas y verificables: ningún precio promocional puede estar por debajo del costo más el margen mínimo; no puede haber más de dos promociones simultáneas por producto y zona; y las promociones del canal moderno relacionadas con acuerdos trimestrales requieren revisión jurídica. Una regla programada ofrece mayor consistencia y trazabilidad que un modelo. |

## Apéndices (obligatorios, no puntuados)

### A. Contribución del equipo

La distribución se realizó considerando la extensión y complejidad de cada sección. Carlos Alcántar fue responsable de las secciones 1. Objetivo delegado y 3. Poder otorgado, además de crear el documento compartido y organizar la reunión inicial. Rodrigo Robledo trabajó en la sección 2. Margen de decisión. David Hernández fue responsable de la sección 4. Acciones irreversibles, además de coordinar la revisión y discusión final del contenido. Finalmente, Cesar Avila desarrolló la sección 5. Responsabilidad y Model Decision Card.

Es importante resaltar que se utilizó una estrategia de revisión conjunta. Aunque se asignaron responsables principales para desarrollar cada parte del contrato, los cuatro integrantes revisamos, discutimos y propusimos cambios al contenido completo antes de integrar la versión final.

La decisión más discutida estuvo relacionada con el alcance que debía tener el agente al formular recomendaciones comerciales:

Primero, se debatió si el asistente debía poder proponer modificaciones a los acuerdos comerciales. Después de revisar el caso, el equipo determinó que el agente puede identificar conflictos, analizar su impacto y proporcionar información para su revisión, pero no debe proponer ni decidir modificaciones sobre dichos acuerdos, debido a sus implicaciones comerciales y jurídicas.

También se discutió el nivel de aplicación de las recomendaciones y promociones, ya que el caso hace referencia a decisiones por tienda y zona, pero la operación está estructurada también en cuatro canales de venta. Tras analizar esta estructura, se decidió permitir que el asistente genere recomendaciones a nivel de tienda, zona o canal, siempre que exista evidencia suficiente para sustentar ese nivel de análisis y que la decisión final permanezca bajo responsabilidad humana.

### B. Declaración de uso de IA

Usar IA es opcional. Se declara con honestidad su uso o no uso en tres líneas:

**Qué le delegamos:** qué partes hizo la IA y con qué herramienta, o si no se utilizó IA.

Se utilizó ChatGPT para generar una propuesta que sirviera de guía para el caso y se seleccionó aquello que coincidió con las ideas generales consensuadas con el equipo.

**Qué verificamos:** qué revisamos contra el caso, el dataset o las lecciones antes de aceptarlo.

Solo se utilizaron el caso de ejemplo y el caso descrito, sin los datasets. Cada pregunta fue revisada por todos los integrantes para estar de acuerdo con el contenido.

**Qué corregimos:** qué ajustamos tras verificar. Si no se detectaron errores, indicarlo y explicar qué se comprobó; no hay que inventar una corrección.

Ajustamos el margen de decisión del agente, ya que ninguna acción con impacto externo deberá quedar automatizada. Por ello, reforzamos los mecanismos de protección para contar siempre con aprobaciones, protección de datos y trazabilidad de la información.
