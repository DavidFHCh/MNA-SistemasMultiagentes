"""Propuestas de ruta para el laboratorio. Nunca escribe en la bandeja ni evalúa código."""
import hashlib
import json
import urllib.error
import urllib.request
import uuid

BASE = "https://aula.gluber.link"
MODELO = "gpt-5.6-luna"
RUTAS = {"aceptada", "rechazada_precondicion", "rechazada_duplicado", "escalada"}
_cache = {}
_intentos = set()


def ruta_por_reglas(caso):
    """Reglas del caso: existencia, duplicado, conflicto; en ese orden."""
    if not caso["tienda_valida"] or not caso["producto_valido"]:
        return "rechazada_precondicion"
    if caso["duplicado"]:
        return "rechazada_duplicado"
    if caso["conflicto"]:
        return "escalada"
    return "aceptada"


def casos_seguros(casos):
    campos = {"id", "tienda_valida", "producto_valido", "duplicado", "conflicto"}
    if not isinstance(casos, list) or len(casos) != 4:
        raise ValueError("Se esperan los cuatro casos del laboratorio.")
    limpio = []
    for i, c in enumerate(casos, 1):
        if not isinstance(c, dict) or set(c) != campos or type(c["id"]) is not int or c["id"] != i:
            raise ValueError("El caso cambió su esquema o su identificador.")
        if any(type(c[k]) is not bool for k in campos - {"id"}):
            raise ValueError("Las condiciones del caso deben ser verdaderas o falsas.")
        limpio.append(dict(c))
    return limpio


def validar_propuestas(datos):
    """Valida estructura, no acierto. Una ruta equivocada sigue siendo evidencia a analizar."""
    if not isinstance(datos, dict) or set(datos) != {"propuestas"}:
        raise ValueError("Formato no válido: se esperaba el objeto propuestas.")
    filas = datos["propuestas"]
    if not isinstance(filas, list) or len(filas) != 4:
        raise ValueError("Se requieren cuatro propuestas, una por caso.")
    for i, fila in enumerate(filas, 1):
        if not isinstance(fila, dict) or set(fila) != {"id", "ruta", "motivo"}:
            raise ValueError("La propuesta debe contener solo id, ruta y motivo.")
        if type(fila["id"]) is not int or fila["id"] != i:
            raise ValueError("Identificador repetido, cambiado o fuera de orden.")
        if not isinstance(fila["ruta"], str) or fila["ruta"] not in RUTAS:
            raise ValueError("Ruta fuera del catálogo; no se autoriza ninguna acción.")
        if not isinstance(fila["motivo"], str) or not 1 <= len(fila["motivo"].strip()) <= 1200:
            raise ValueError("El motivo debe ser texto breve no vacío.")
    return [dict(f) for f in filas]


def _enviar(payload, clave, identificador):
    class SinRedireccion(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None
    solicitud = urllib.request.Request(
        BASE + "/v1/chat/completions", data=json.dumps(payload).encode(), method="POST",
        headers={"Authorization": "Bearer " + clave, "Content-Type": "application/json",
                 "Idempotency-Key": identificador})
    try:
        with urllib.request.build_opener(SinRedireccion).open(solicitud, timeout=90) as r:
            cuerpo=r.read(200001)
            if len(cuerpo)>200000:
                raise ValueError("Respuesta demasiado extensa")
            return json.loads(cuerpo.decode())
    except urllib.error.HTTPError as e:
        mensajes = {401: "Clave inválida o vencida", 403: "Acceso no autorizado",
                    402: "Saldo insuficiente", 409: "Solicitud ya registrada",
                    429: "Límite temporal o de consumo"}
        raise RuntimeError(mensajes.get(e.code, "El servicio respondió HTTP " + str(e.code)) +
                           ". No hubo reintento automático. Continúa sin_api y consulta el portal.") from None
    except Exception:
        raise RuntimeError("No se recibió una respuesta completa. No repitas la consulta: revisa tu "
                           "consumo en el portal y continúa sin_api. No compartas tu clave.") from None


def proponer_rutas(casos, modo="sin_api", clave=None, transporte=None):
    casos = casos_seguros(casos)
    if modo == "sin_api":
        motivos = {"aceptada": "Cumple existencia, no está duplicado y no presenta conflicto.",
                   "rechazada_precondicion": "El identificador no cumple el catálogo del ejercicio.",
                   "rechazada_duplicado": "El caso ya se registró; no se vuelve a escribir.",
                   "escalada": "El conflicto requiere revisión humana; no se escribe."}
        propuestas = [{"id": c["id"], "ruta": ruta_por_reglas(c),
                       "motivo": motivos[ruta_por_reglas(c)]} for c in casos]
        return propuestas, {"modo": modo, "origen": "reglas locales, no modelo",
                            "llamadas": 0, "tokens_entrada": 0, "tokens_salida": 0}
    if modo != "luna_api":
        raise ValueError("MODO debe ser sin_api o luna_api.")
    if not isinstance(clave, str) or not clave.startswith("ag_") or any(c.isspace() for c in clave):
        raise ValueError("Introduce tu clave personal ag_ del Aula, no una clave de Azure.")
    payload = {"model": MODELO, "max_completion_tokens": 1200, "stream": False,
        "messages": [{"role": "system", "content":
            "Eres el enrutador de un ejercicio académico. No ejecutas herramientas. "
            "Para cada caso aplica en orden: si tienda_valida o producto_valido es false, "
            "rechazada_precondicion; si duplicado es true, rechazada_duplicado; si conflicto es true, "
            "escalada; en otro caso, aceptada. No inventes condiciones. Devuelve solo JSON, sin Markdown, "
            "con clave propuestas: lista de cuatro objetos en orden con id, ruta y motivo "
            "(una frase en español). Conserva los id. No puedes autorizar acciones externas."},
            {"role": "user", "content": json.dumps(casos)}]}
    huella = hashlib.sha256((clave + json.dumps(payload, sort_keys=True)).encode()).hexdigest()
    if huella in _cache:
        propuestas, meta = _cache[huella]
        return [dict(f) for f in propuestas], dict(meta, reutilizada=True)
    if huella in _intentos:
        raise RuntimeError("Esta consulta ya se intentó en esta sesión. No se reenvió. "
                           "Consulta el portal; puedes continuar sin_api.")
    _intentos.add(huella)
    respuesta = (transporte or _enviar)(payload, clave, str(uuid.uuid4()))
    try:
        choice = respuesta["choices"][0]
        if choice.get("finish_reason") != "stop":
            raise ValueError()
        propuestas = validar_propuestas(json.loads(choice["message"]["content"]))
    except (KeyError, IndexError, TypeError, ValueError):
        raise ValueError("Respuesta incompleta o fuera del esquema. No se ejecutó ninguna acción "
                         "por instrucción del modelo. Documenta el incidente y continúa sin_api.") from None
    uso = respuesta.get("usage") or {}
    if not isinstance(uso, dict):
        uso = {}
    meta = {"modo": modo, "origen": "Luna por Aula Gateway", "modelo": MODELO,
            "llamadas": 1, "tokens_entrada": uso.get("prompt_tokens"),
            "tokens_salida": uso.get("completion_tokens"), "reutilizada": False}
    _cache[huella] = ([dict(f) for f in propuestas], dict(meta))
    return propuestas, meta
