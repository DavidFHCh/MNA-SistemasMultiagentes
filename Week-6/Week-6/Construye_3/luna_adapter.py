"""Dos modalidades para el mismo caso. No ejecuta acciones ni conserva claves."""
import hashlib
import json
import urllib.request
import urllib.error
import uuid

URL = "https://aula.gluber.link/v1/chat/completions"
MODELO = "gpt-5.6-luna"
_solicitudes = {}
_respuestas = {}

def propuesta_local(evidencia):
    return {"tienda_id": evidencia["tienda_id"], "producto_id": evidencia["producto_id"],
            "accion": "preparar_borrador", "requiere_revision": True,
            "fuentes": ["inventarios.csv"],
            "explicacion": "Se observaron días sin inventario en la ventana histórica. Preparar un borrador para revisión; no emitir un pedido."}

def validar_propuesta(p, evidencia):
    campos = {"tienda_id", "producto_id", "accion", "requiere_revision", "fuentes", "explicacion"}
    if not isinstance(p, dict) or set(p) != campos:
        raise ValueError("La propuesta no cumple el formato. No se ejecutó ninguna acción.")
    if any(p[k] != evidencia[k] for k in ("tienda_id", "producto_id")):
        raise ValueError("La propuesta cambió los identificadores del caso. Se bloqueó.")
    if p["accion"] != "preparar_borrador" or p["requiere_revision"] is not True:
        raise ValueError("La propuesta excede el permiso de preparar un borrador para revisión.")
    if p["fuentes"] != ["inventarios.csv"]:
        raise ValueError("La propuesta cita una fuente no incluida en el paquete enviado.")
    if not isinstance(p["explicacion"], str) or not 1 <= len(p["explicacion"].strip()) <= 1200:
        raise ValueError("Falta una explicación breve. No se ejecutó ninguna acción.")
    return p

def _enviar(payload, clave, identificador):
    req = urllib.request.Request(URL, data=json.dumps(payload).encode(), method="POST",
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + clave,
                 "Idempotency-Key": identificador})
    # Sin redirecciones: una clave nunca debe reenviarse a otro destino.
    class SinRedireccion(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None
    try:
        with urllib.request.build_opener(SinRedireccion).open(req, timeout=65) as r:
            return json.loads(r.read(200000).decode())
    except urllib.error.HTTPError as e:
        mensajes = {401: "Clave inválida o vencida.", 403: "Acceso no autorizado.",
                    402: "Saldo insuficiente.", 409: "Solicitud ya registrada; consulta su estado antes de repetir.",
                    429: "Límite temporal o de consumo alcanzado."}
        raise RuntimeError(mensajes.get(e.code, f"El servicio respondió HTTP {e.code}.") +
            " No hay reintentos automáticos. Puedes seleccionar sin_api y repetir desde la preparación.") from None
    except Exception:
        raise RuntimeError("No se obtuvo una respuesta completa. No se ejecutó ninguna acción. "
            "No repitas con otra clave de idempotencia: verifica el consumo o usa sin_api. "
            "No incluyas tu clave en capturas ni mensajes de soporte.") from None

def proponer(evidencia, modo="sin_api", clave=None, transporte=None):
    if modo not in {"sin_api", "luna_api"}:
        raise ValueError("MODO debe ser sin_api o luna_api.")
    if modo == "sin_api":
        return validar_propuesta(propuesta_local(evidencia), evidencia), {"modo": modo, "llamadas": 0}
    if not isinstance(clave, str) or not clave.startswith("ag_"):
        raise ValueError("Usa únicamente la clave individual de Aula Gateway. No una clave maestra ni la de un compañero.")
    # Lista cerrada: no enviar comentarios libres, credenciales ni filas del portal.
    campos = ("tienda_id", "producto_id", "dias_cero", "corte", "ventana_historica_dias")
    seguro = {k: evidencia[k] for k in campos}
    payload = {"model": MODELO, "max_completion_tokens": 800, "stream": False,
        "messages": [
            {"role": "system", "content": "Eres un asistente de análisis de inventario en un ejercicio académico. "
             "Usa solo los datos suministrados. Devuelve exclusivamente un objeto JSON con los campos tienda_id, "
             "producto_id, accion (preparar_borrador), requiere_revision (true), fuentes ([inventarios.csv]) "
             "y explicacion (una o dos frases en español). No inventes ventas, precios, causas ni cantidades a pedir. "
             "No tienes permiso para emitir pedidos. Conserva exactamente los identificadores recibidos."},
            {"role": "user", "content": json.dumps(seguro, ensure_ascii=False)}]}
    # Huella solo en memoria, ligada a la cuenta y al cuerpo. Nunca se imprime ni se guarda la clave.
    huella = hashlib.sha256((clave + json.dumps(payload, sort_keys=True)).encode()).hexdigest()
    if huella in _respuestas:
        p, meta = _respuestas[huella]
        return dict(p), dict(meta, reutilizada=True)
    identificador = _solicitudes.setdefault(huella, str(uuid.uuid4()))
    respuesta = (transporte or _enviar)(payload, clave, identificador)
    try:
        choice = respuesta["choices"][0]
        if choice.get("finish_reason") != "stop":
            raise ValueError("Respuesta incompleta o no textual.")
        p = json.loads(choice["message"]["content"])
    except (KeyError, IndexError, TypeError, ValueError):
        raise ValueError("Luna no entregó un JSON completo. Conserva esta observación como resultado; "
                         "no se ejecutó ninguna acción. Usa sin_api si necesitas continuar.") from None
    p = validar_propuesta(p, evidencia)
    usage = respuesta.get("usage", {})
    meta = {"modo": modo, "modelo": MODELO, "llamadas": 1,
            "tokens_entrada": usage.get("prompt_tokens"), "tokens_salida": usage.get("completion_tokens"),
            "reutilizada": False}
    _respuestas[huella] = (dict(p), dict(meta))
    return p, meta
