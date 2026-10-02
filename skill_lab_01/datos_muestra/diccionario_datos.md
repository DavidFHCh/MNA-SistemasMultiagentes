# Diccionario de datos — Distribuidora Cuauhtemoc
Derivado de: 01_source/SHARED_SPECS.md v1.0 | Generado: 2026-07-19 | Proceso: generate_dataset.py | Estado: probado (muestra + v01-v03)

| Tabla | Campo | Tipo | Descripcion | Regla de integridad |
|---|---|---|---|---|
| tiendas | tienda_id | str (T####) | Identificador unico | Llave primaria |
| tiendas | canal | enum | moderno, conveniencia, mayoreo, tradicional | Distribucion 40/30/10/120 (escala completa) |
| tiendas | zona | enum | Norte, Centro, Bajio, Sur | — |
| tiendas | tam | enum | A, B, C | Multiplicadores 1.6/1.0/0.55 |
| tiendas | frecuencia_visita | enum | semanal o quincenal; vacio fuera del tradicional | — |
| tiendas | preventista_id | str (PREV-###) | Preventista asignado | Vacio en moderno y mayoreo |
| productos | producto_id | str (P###) | Identificador unico | Llave primaria |
| productos | categoria | enum | botanas, galletas, abarrotes, cuidado_personal | 18/12/12/18 |
| productos | costo / precio_lista | float MXN | Costo y precio de lista | precio_lista > costo |
| productos | margen_minimo_pct | int | Margen minimo por politica comercial | 12, 15 o 18 |
| productos | rotacion_esperada | float | Unidades/semana en tienda tamano B | Base de la demanda Poisson |
| ventas | fecha, tienda_id, producto_id | — | Grano: dia-tienda-producto | FK a tiendas y productos |
| ventas | unidades | int > 0 | Venta del dia | Limitada por inventario |
| ventas | precio_efectivo | float | Precio cobrado | = precio_lista salvo promocion |
| inventarios | unidades_disponibles | int >= 0 | Inventario observado | Diario (portal) o dia de visita (preventa) |
| inventarios | fuente | enum | portal / preventa | portal solo moderno y conveniencia |
| precios_competencia | precio_capturado | float | Precio del competidor capturado en visita | 6% con error tipografico sembrado |
| precios_competencia | comentario | str libre | Campo libre del preventista | Contiene las filas de inyeccion (A5) |
| promociones | tipo / valor / estado | enum | descuento_pct, 2x1, precio_fijo | Reglas comerciales en SHARED_SPECS A.2 |
| visitas | duracion_min, pedido_levantado | int, bool | Registro de visita | Solo tradicional y conveniencia |
| anomalias_sembradas | tipo | enum | A1..A6 | Solo kit docente; no se publica a alumnos |
