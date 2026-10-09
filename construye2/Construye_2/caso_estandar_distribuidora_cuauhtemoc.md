# Caso estándar | Distribuidora Cuauhtémoc

## A.1 La empresa

Distribuidora Cuauhtémoc es una empresa mexicana de consumo masivo con dos categorías: alimentos empacados (botanas, galletas, abarrotes secos) y cuidado personal. Opera una planta, seis centros de distribución regionales y una fuerza de ventas de 340 preventistas. Factura alrededor de 4,800 millones de pesos anuales. Sus marcas compiten contra dos multinacionales y una creciente marca propia de los autoservicios.

Vende por cuatro canales. El canal moderno (autoservicios nacionales) representa el 34 por ciento de la venta y opera con pedidos electrónicos y acuerdos comerciales trimestrales. El mayoreo (18 por ciento) surte a distribuidores secundarios. Las cadenas de conveniencia (16 por ciento) exigen cumplimiento estricto de planograma y tienen penalizaciones por quiebre. El canal tradicional (32 por ciento) son 41,000 tiendas de barrio atendidas por preventistas con visita semanal o quincenal; es el canal con mayor margen y el más difícil de observar: la única señal confiable es lo que el preventista captura en su terminal durante la visita.

## A.2 Las tres decisiones comerciales

El equipo comercial vive de tres decisiones que hoy se toman con análisis manual y llegan tarde.

### Detección de quiebres

Un quiebre de anaquel (la tienda no tiene el producto que debería tener) cuesta la venta y, repetido, cede el espacio a la competencia. En el canal moderno hay datos diarios de venta e inventario por tienda; en el tradicional solo la foto semanal del preventista. Hoy un analista tarda dos a tres días en cruzar ventas, inventarios y cumplimiento; cuando la alerta llega, el quiebre lleva una semana.

### Calibración de promociones

Las promociones se autorizan por zona y canal. Una promoción mal calibrada destruye margen o provoca compras especulativas del mayoreo que canibalizan al tradicional. Las reglas comerciales vigentes: ningún precio promocional por debajo del costo más el margen mínimo por categoría; máximo dos promociones simultáneas por producto y zona; toda promoción al canal moderno requiere revisión del área jurídica si coincide con acuerdos trimestrales.

### Reacción a la competencia

Los preventistas capturan precios de dos competidores en cada visita. Esa señal es valiosa y sucia: llega con retraso, con errores de captura y con huecos en las tiendas no visitadas.

## A.3 El encargo

La dirección comercial aprobó explorar un asistente agéntico de inteligencia comercial. Su propósito: observar las señales de venta, inventario y competencia; detectar anomalías; investigar causas probables; y proponer acciones concretas por tienda o zona, preparando el caso para que un humano decida.

La dirección fue explícita en tres restricciones:

1. Ninguna comunicación de precio sale al mercado sin aprobación humana.
2. Los datos por tienda del canal moderno están protegidos por convenios de confidencialidad con las cadenas y no pueden salir de la infraestructura autorizada.
3. El sistema debe dejar rastro auditable de cada recomendación: qué vio, qué concluyó y qué propuso.

## A.4 Actores y sistemas

**Actores:** director comercial (autoriza), cuatro gerentes de zona (deciden promociones y despachan alertas), 340 preventistas (ejecutan en campo y capturan datos), un analista comercial senior (hoy hace el cruce manual; será el operador del asistente), área jurídica (revisa promociones del canal moderno), área de datos (custodia los convenios de confidencialidad).

**Sistemas:** ERP con ventas facturadas por día, producto y cliente; el sistema de preventa con las capturas de campo (inventario visto, precios de competencia, pedido levantado); el maestro de productos y precios; el calendario promocional; y los portales de las cadenas del canal moderno con venta e inventario por tienda (acceso de solo lectura, bajo convenio).

## A.5 Alcance y límites del proyecto académico

Los equipos del curso diseñan y construyen el asistente por etapas sobre un dataset sintético que reproduce esta operación a escala reducida (200 tiendas, 60 productos, 13 semanas). El alcance de cada etapa lo define el módulo correspondiente. Los límites son parte del aprendizaje: qué decide solo el asistente, qué propone y qué tiene prohibido es exactamente la primera entrega (el contrato de delegación), y el capstone del módulo 5 rinde cuentas contra ese contrato.

## A.6 Riesgos del dominio (para análisis en los módulos)

- Una recomendación de precio equivocada es difícil de revertir una vez comunicada (M1, irreversibles).
- La señal de competencia es dudosa y envejece (M3, evidencia y vigencia).
- Precio, inventario y promoción pueden recomendar acciones contradictorias (M4, arbitraje).
- Una promoción mal dirigida puede violar acuerdos comerciales (M5, gobierno).
- Los datos de las cadenas son confidenciales por convenio (M1 y M5, poder y privacidad).
- El preventista necesita respuestas en segundos durante la visita (M1, latencia).

---

## Los datos que usará tu equipo

El dataset sintético reproduce la operación a escala reducida: 200 tiendas, 60 productos y 13 semanas, en siete tablas: tiendas, productos, ventas, inventarios, precios de competencia, promociones y visitas de preventa. El diccionario de datos con la definición de cada campo viene incluido en el archivo de muestra descargable de esta página.

Para explorar la estructura de los datos, puedes usar la muestra descargable. A partir de Construye 2, todos los equipos trabajan con un mismo conjunto completo de datos; no se asignan códigos ni versiones por número de equipo. Cada equipo conserva su contrato y justifica sus propias decisiones. Recuerda la restricción del caso: los datos por tienda del canal moderno se tratan como confidenciales bajo convenio, y tu sistema deberá demostrarlo desde el módulo 3.
