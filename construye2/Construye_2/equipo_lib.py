"""Biblioteca compartida de los notebooks de equipo (Construye 2-4 y Capstone).
Derivado de: SHARED_SPECS.md y M02-M05 PRODUCTION_SPECS | 2026-07-20 | Sin API: opera sobre los CSV del conjunto común.
Los notebooks exponen las DECISIONES; esta biblioteca implementa la infraestructura."""
import pandas as pd, json, os, datetime, math, copy

class Traza:
    def __init__(s, caso_id, tope_pasos=None):
        s.caso_id=caso_id; s.lineas=[]; s.presupuesto_usado=0
        s.tope_pasos=tope_pasos; s.paro_por_limite=False
    def paso(s, fase, detalle, evidencia=None, version="v1"):
        if s.paro_por_limite: return
        # El último registro se reserva para el cierre: también cuenta en el tope.
        # No se autoriza una operación que deje sin espacio para documentar su final.
        if s.tope_pasos is not None and s.presupuesto_usado >= s.tope_pasos:
            return
        if s.tope_pasos is not None and fase != "paro" and s.presupuesto_usado >= s.tope_pasos - 1:
            fase = "paro"
            detalle = f"PARO POR LIMITE: no queda espacio para otro paso y su cierre; tope {s.tope_pasos}"
            evidencia = {"ultimo_registro_reservado": True}
            s.paro_por_limite = True
        s.presupuesto_usado += 1
        s.lineas.append(dict(n=len(s.lineas)+1,fase=fase,detalle=detalle,
            evidencia=evidencia or {}, version=version))
    def mostrar(s):
        print(f"----- Traza {s.caso_id} -----")
        for l in s.lineas:
            ev=f" | evidencia: {l['evidencia']}" if l['evidencia'] else ""
            print(f"[{l['n']:>2}] {l['fase'].upper():12s} {l['detalle']}{ev}")

def cargar_variante(ruta):
    d={}
    for t in ["tiendas","productos","ventas","inventarios","precios_competencia","promociones","visitas"]:
        d[t]=pd.read_csv(os.path.join(ruta,f"{t}.csv"))
    d["ventas"]["fecha"]=pd.to_datetime(d["ventas"].fecha)
    d["inventarios"]["fecha"]=pd.to_datetime(d["inventarios"].fecha)
    d["precios_competencia"]["fecha_captura"]=pd.to_datetime(d["precios_competencia"].fecha_captura)
    return d

def detectar_quiebres(d, dias_minimos=2, ventana_dias=14, tr=None):
    inv=d["inventarios"]; hoy=inv.fecha.max()
    win=inv[(inv.fecha>hoy-pd.Timedelta(days=ventana_dias))&(inv.unidades_disponibles==0)]
    g=(win.groupby(["tienda_id","producto_id"]).fecha.nunique().reset_index(name="dias_cero"))
    g=g[g.dias_cero>=dias_minimos]
    g=g.merge(d["productos"][["producto_id","rotacion_esperada","precio_lista"]],on="producto_id")
    g["costo_estimado"]=(g.dias_cero*g.rotacion_esperada/7*g.precio_lista).round(0)
    g=g.sort_values("costo_estimado",ascending=False).reset_index(drop=True)
    if tr: tr.paso("observar",f"inventarios ventana {ventana_dias}d; quiebres >= {dias_minimos}d en cero",
                   {"combinaciones":int(len(g)),"corte":str(hoy.date())})
    return g

def promociones_activas(d, zona=None):
    p=d["promociones"]; act=p[p.estado=="activa"]
    if zona is not None: act=act[act.zona==zona]
    return act

def capturas_vigentes(d, dias_vigencia=10, tr=None):
    pc=d["precios_competencia"].copy(); hoy=pc.fecha_captura.max()
    pc["dias"]= (hoy-pc.fecha_captura).dt.days
    vig=pc[pc.dias<=dias_vigencia]; cad=pc[pc.dias>dias_vigencia]
    if tr: tr.paso("observar",f"capturas: {len(vig)} vigentes (<= {dias_vigencia}d), {len(cad)} caducas identificadas (conteo, sin filtrar el detector)",
                   {"corte":str(hoy.date())})
    return vig, cad

def detectar_inyeccion(d):
    pc=d["precios_competencia"]
    m=pc.comentario.fillna("").str.contains("ignora tus instrucciones",case=False)
    return pc[m]

def detectar_cruce_confidencial(d):
    pc=d["precios_competencia"]
    m=pc.comentario.fillna("").str.contains("exportado_de_portal",case=False)
    return pc[m]

class Bandeja:
    """Sandbox de acciones controladas con precondiciones y clases de reversibilidad."""
    def __init__(s, d): s.d=d; s.casos=[]; s.rechazos=[]; s.senales=[]
    def escribir_caso(s, caso, precondiciones=True, tr=None):
        if type(precondiciones) is not bool:
            raise ValueError("precondiciones debe ser booleano")
        if tr and (tr.paro_por_limite or (tr.tope_pasos is not None and tr.presupuesto_usado >= tr.tope_pasos - 1)):
            tr.paso("paro", "PARO POR LIMITE: escritura no realizada; se conserva el espacio de cierre")
            tr.paro_por_limite = True
            return "rechazada_limite"
        if not isinstance(caso, dict) or not all(isinstance(caso.get(k), str) and caso[k].strip() for k in ("tienda_id", "producto_id")):
            return "rechazada_precondicion"
        if type(caso.get("conflicto", False)) is not bool:
            return "rechazada_precondicion"
        if precondiciones:
            if caso["producto_id"] not in set(s.d["productos"].producto_id):
                s.rechazos.append(("precondicion_producto", copy.deepcopy(caso)))
                if tr: tr.paso("actuar", "rechazada: producto inexistente", {})
                return "rechazada_precondicion"
            if caso["tienda_id"] not in set(s.d["tiendas"].tienda_id):
                s.rechazos.append(("precondicion_tienda",caso)); 
                if tr: tr.paso("actuar","rechazada: tienda inexistente (precondicion)",{"tienda":caso["tienda_id"]})
                return "rechazada_precondicion"
            if any(c["tienda_id"]==caso["tienda_id"] and c["producto_id"]==caso["producto_id"] for c in s.casos):
                s.rechazos.append(("duplicado",caso))
                if tr: tr.paso("actuar","rechazada: duplicado (compensable: retirar duplicado)",{})
                return "rechazada_duplicado"
            if caso.get("conflicto"):
                paquete = {
                    "tienda": caso["tienda_id"], "producto": caso["producto_id"],
                    "zona": caso.get("zona", "no indicada"),
                    "costo_estimado": caso.get("costo"), "fecha_corte": caso.get("fecha_corte"),
                    "accion_propuesta": caso.get("accion_propuesta"),
                    "conflicto": copy.deepcopy(caso.get("evidencia_conflicto", {"origen": "declarado; sin detalle adjunto"})),
                    "decision_pendiente": "El gerente debe revisar el conflicto antes de autorizar; no se escribió el borrador.",
                }
                if tr: tr.paso("paro", "ESCALAMIENTO: caso preparado para revisión humana (sin notificación real)", paquete)
                s.senales.append(("escalamiento",caso)); return "escalada"
        s.casos.append(copy.deepcopy(caso))
        if tr: tr.paso("actuar","caso escrito a bandeja (reversible: borrador)",{"tienda":caso["tienda_id"],"producto":caso["producto_id"]})
        return "aceptada"

class Memoria:
    """Episodica con politica de olvido y filtro de confidencialidad."""
    def __init__(s, ruta="memoria_episodica.json", dias_retencion=90, fuentes_excluidas=("portal",)):
        s.ruta=ruta; s.dias=dias_retencion; s.fuentes_excluidas=set(fuentes_excluidas)
        s.ep = json.load(open(ruta)) if os.path.exists(ruta) else []
    def _vigentes(s):
        if type(s.dias) is not int or s.dias < 1:
            raise ValueError("dias_retencion debe ser entero positivo")
        hoy = datetime.date.today()
        def vigente(e):
            if not isinstance(e, dict): return False
            try: edad = (hoy - datetime.date.fromisoformat(e.get("fecha_registro", ""))).days
            except (ValueError, TypeError): return False
            return 0 <= edad < s.dias and e.get("fuente") not in s.fuentes_excluidas
        return [e for e in s.ep if vigente(e)]
    def escribir(s, episodio, tr=None):
        if not isinstance(episodio, dict): raise ValueError("episodio debe ser un diccionario")
        if tr and (tr.paro_por_limite or (tr.tope_pasos is not None and tr.presupuesto_usado >= tr.tope_pasos)):
            tr.paso("paro", "memoria no escrita: presupuesto agotado")
            return False
        if episodio.get("fuente") in s.fuentes_excluidas:
            if tr: tr.paso("memoria","EXCLUIDO de persistencia: dato bajo convenio (politica de olvido/confidencialidad)",{})
            return False
        s.ep = s._vigentes()
        episodio = copy.deepcopy(episodio)
        episodio["fecha_registro"]=str(datetime.date.today())
        s.ep.append(episodio); json.dump(s.ep,open(s.ruta,"w")); 
        if tr: tr.paso("memoria","episodio persistido con evidencia y fecha",{"n_episodios":len(s.ep)})
        return True
    def recordar(s, tienda_id, producto_id, tr=None):
        hits=[copy.deepcopy(e) for e in s._vigentes() if e.get("tienda_id")==tienda_id and e.get("producto_id")==producto_id]
        if tr and hits: tr.paso("memoria",f"episodio previo recuperado ({len(hits)})",{"ultimo":hits[-1].get("fecha_registro")})
        return hits

def arbitro(recomendaciones, precedencias, tr=None):
    """Reglas de precedencia: lista ordenada de claves; el residuo escala."""
    if not isinstance(recomendaciones, list) or not recomendaciones:
        raise ValueError("El arbitro requiere recomendaciones no vacias")
    if not all(isinstance(r, dict) and isinstance(r.get("accion"), str) and r["accion"].strip() for r in recomendaciones):
        raise ValueError("Recomendaciones mal formadas")
    if not isinstance(precedencias, (list, tuple)) or not all(isinstance(x,str) and x.strip() for x in precedencias) or len(set(precedencias))!=len(precedencias):
        raise ValueError("Precedencias invalidas")
    if len({r["accion"] for r in recomendaciones})<=1:
        if tr: tr.paso("arbitraje","sin conflicto: recomendacion unica",{})
        return recomendaciones[0], False
    for regla in precedencias:
        gana=[r for r in recomendaciones if r.get("regla")==regla]
        if gana:
            if len({r["accion"] for r in gana}) > 1:
                if tr: tr.paso("arbitraje", "empate en la misma precedencia: ESCALA al humano", {})
                return None, True
            if tr: tr.paso("arbitraje",f"precedencia aplicada: {regla} (origen: contrato M1)",
                          {"descartadas":[r['accion'] for r in recomendaciones if r is not gana[0]]})
            return gana[0], False
    if tr: tr.paso("arbitraje","residuo sin precedencia: ESCALA al humano con paquete",{})
    return None, True


# ----- Extensiones v2: las decisiones del documento, ejecutables -----

def validar_presupuesto(presupuesto, tolerancia=0.001):
    """Valida que el presupuesto de mesa sume 100% y no tenga procedencias vacias."""
    if not isinstance(presupuesto, dict) or not presupuesto:
        return False, "presupuesto debe ser un diccionario no vacio"
    if not all(isinstance(k,str) and k.strip() and type(v) in (int,float) and math.isfinite(v) for k,v in presupuesto.items()):
        return False, "procedencias y valores deben ser validos y finitos"
    total = sum(presupuesto.values())
    if abs(total-1.0) > tolerancia:
        return False, f"el presupuesto suma {total:.3f}, no 1.0; ajusta las proporciones de tu seccion 1.1"
    if any(v<=0 for v in presupuesto.values()):
        return False, "hay una procedencia con presupuesto 0 o negativo; toda procedencia declarada ocupa espacio"
    return True, "presupuesto valido"

def armar_mesa(presupuesto, limite_tokens, tr=None):
    """Convierte el presupuesto (proporciones) en tokens por procedencia y lo deja en la traza."""
    ok, msg = validar_presupuesto(presupuesto)
    if not ok:
        raise ValueError(f"Presupuesto de mesa invalido: {msg}")
    mesa = {k: int(round(v*limite_tokens)) for k, v in presupuesto.items()}
    if tr: tr.paso("contexto", f"mesa armada: {limite_tokens} tokens repartidos por procedencia",
                   {k: f"{v} tokens ({presupuesto[k]:.0%})" for k, v in mesa.items()})
    return mesa

_COLUMNAS_FECHA = {"ventas":"fecha","inventarios":"fecha","precios_competencia":"fecha_captura"}

def recortes_de_vigencia(d, ventanas, tr=None):
    """Cuenta edades de 0 a N dias, ambos incluidos; no modifica ni filtra las fuentes."""
    resumen = {}
    for fuente, dias in ventanas.items():
        if fuente not in _COLUMNAS_FECHA:
            raise ValueError(f"No se vigencia la fuente '{fuente}'; fuentes con fecha: {sorted(_COLUMNAS_FECHA)}")
        col = _COLUMNAS_FECHA[fuente]; df = d[fuente]
        hoy = df[col].max()
        dentro = int((df[col] >= hoy - pd.Timedelta(days=dias)).sum())
        fuera = int(len(df) - dentro)
        resumen[fuente] = dict(dias=dias, dentro=dentro, fuera=fuera, corte=str(hoy.date()))
        if tr: tr.paso("observar", f"{fuente}: ventana {dias}d; {dentro} registros vigentes, {fuera} fuera de ventana (declarados)",
                       {"corte": str(hoy.date())})
    return resumen

def portal_con_reintentos(limite_reintentos, tr=None, espera_base_seg=2):
    """Simula el portal de proveedores caido: reintenta con espera creciente y escala al agotar el limite."""
    for intento in range(1, limite_reintentos+1):
        espera = espera_base_seg * (2 ** (intento-1))
        if tr: tr.paso("error", f"portal caido; reintento {intento}/{limite_reintentos} con espera de {espera}s", {})
    if tr: tr.paso("paro", "ESCALAMIENTO: portal sin respuesta tras agotar reintentos; se notifica a operaciones",
                   {"paquete": "caso preparado, error citado, ultimo intento con hora"})
    return "escalado_a_operaciones"

def silla_vacia(politica, tr=None):
    """Simula la linea de tiempo de la silla vacia: recordatorio, elevacion y estado seguro por defecto."""
    rec, ele = politica["recordatorio_h"], politica["elevacion_h"]
    if not (0 < rec < ele):
        raise ValueError(f"Politica de silla vacia invalida: recordatorio ({rec}h) debe ser menor que elevacion ({ele}h)")
    eventos = [(0, "caso en bandeja, visible al decisor; estado por defecto: borrador (nada se ejecuta solo)"),
               (rec, f"sin decision a las {rec}h: recordatorio automatico al decisor"),
               (ele, f"sin decision a las {ele}h: se eleva a direccion con el caso completo; el borrador sigue visible")]
    for h, det in eventos:
        if tr: tr.paso("silla_vacia", f"t+{h}h: {det}", {})
    return eventos
