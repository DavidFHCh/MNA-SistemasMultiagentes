"""PDF de evidencias seleccionadas. No accede a Drive, claves ni variables globales."""
import re
from pathlib import Path
from xml.sax.saxutils import escape


def generar_pdf(datos, destino="SkillLab3_resultados.pdf", grafica=None):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    # La misma fuente de matplotlib da soporte a español, símbolos y flechas.
    from matplotlib import font_manager
    for nombre, peso in (("LabSans", "normal"), ("LabSansBold", "bold")):
        pdfmetrics.registerFont(TTFont(nombre, font_manager.findfont(
            font_manager.FontProperties(family="DejaVu Sans", weight=peso))))
    pdfmetrics.registerFontFamily("LabSans",normal="LabSans",bold="LabSansBold")
    estilos = getSampleStyleSheet()
    estilos.add(ParagraphStyle(name="TextoLab", fontName="LabSans", fontSize=9, leading=13,
                              spaceAfter=6, splitLongWords=True))
    estilos.add(ParagraphStyle(name="TituloLab", fontName="LabSansBold", fontSize=19, leading=24,
                              textColor=colors.HexColor("#154e97"), spaceAfter=14))
    estilos.add(ParagraphStyle(name="SeccionLab", fontName="LabSansBold", fontSize=12, leading=17,
                              textColor=colors.HexColor("#154e97"), spaceBefore=14, spaceAfter=8, keepWithNext=True))
    def limpio(valor):
        texto = str(valor)
        # Defensa adicional si alguien pegó una clave en una respuesta libre.
        texto = re.sub(r"\bag_[A-Za-z0-9_\-]+", "[CLAVE OMITIDA]", texto)
        texto = re.sub(r"(?i)Bearer\s+\S+", "[CREDENCIAL OMITIDA]", texto)
        return "".join(c for c in texto if c in "\n\t" or ord(c) >= 32)
    def p(texto, estilo="TextoLab"):
        return Paragraph(escape(limpio(texto)).replace("\n", "<br/>"), estilos[estilo])
    elementos = [p("Skill Lab 3", "TituloLab"), p("Evidencia, recuperación y acciones controladas"),
                 p("Alumno: " + datos.get("alumno", "Sin nombre indicado")),
                 p("Modalidad realizada: " + datos["modalidad"])]
    pendientes = datos.get("pendientes", [])
    if pendientes:
        elementos += [p("BORRADOR: hay campos pendientes. No entregues esta versión."),
                      p("\n".join(pendientes))]
    def titulo(t):
        elementos.append(p(t,"SeccionLab"))
    def tabla(filas, anchos):
        t = Table([[p(c) for c in fila] for fila in filas], colWidths=anchos, repeatRows=1,
                  hAlign="LEFT", splitByRow=1)
        t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#eaf0f8")),
            ("VALIGN",(0,0),(-1,-1),"TOP"),("GRID",(0,0),(-1,-1),.4,colors.HexColor("#c8d2df")),
            ("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),6)]))
        elementos.append(t)
    titulo("1. Resultados técnicos y explicación")
    for i,(nombre,valor) in enumerate(datos["resultados"],1):
        elementos += [p(f"{i}. {nombre}: {valor}"), p("Explicación: "+datos["justificaciones"].get(str(i),"Pendiente"))]
    titulo("2. Comparación de paquetes de contexto")
    elementos.append(p("Datos didácticos precargados; no son mediciones de Luna ni costos de la API."))
    tabla([["Paquete","Fragmentos","Tokens didácticos","Antigüedad"]]+datos["paquetes"], [130,70,110,180])
    if grafica is not None:
        elementos.append(Spacer(1,10))
        elementos.append(Image(grafica,width=480,height=156))
    elementos += [p("Paquete elegido: "+datos["paquete"]), p(datos["por_que"])]
    titulo("3. Registro de ejecución y control de acciones")
    elementos.append(p("La bandeja es una lista en memoria. No se escribieron casos en un sistema externo."))
    for fila in datos["registro"]:
        elementos += [p(f"Caso {fila['id']} - {fila['caso']}"),
                      p(f"Ruta propuesta: {fila['propuesta']}. Veredicto del control: {fila['veredicto']}. "
                        f"Entradas antes/después: {fila['antes']}/{fila['despues']}. Coinciden: {'sí' if fila['coincide'] else 'no'}.")]
        elementos.append(p("Motivo de la propuesta: "+fila["motivo"]))
    elementos.append(p("Consumo de la modalidad realizada: "+datos["consumo"]+
                       ". No confundir con los tamaños precargados de la sección A."))
    if datos.get("incidente"):
        elementos.append(p("Incidente registrado: "+datos["incidente"]))
    titulo("4. Reversibilidad y costo de corrección")
    for nombre,detalle in datos["reversibilidad"].items():
        elementos += [p(nombre+": "+detalle["clase"]),p(detalle["costo_de_corregir"])]
    titulo("5. Conclusiones")
    for nombre,contenido in datos["conclusiones"].items():
        elementos += [p(nombre),p(contenido)]
    titulo("6. Declaración de uso de IA")
    elementos.append(p(datos["declaracion"]))
    titulo("Alcance de esta evidencia")
    elementos.append(p("Este reporte conserva los resultados y respuestas de esta ejecución; no completa respuestas "
        "ni certifica su calidad académica. No hace falta capturar todo el código. Conserva tu notebook como respaldo personal."))
    ruta = Path(destino).resolve()
    if ruta.suffix.lower() != ".pdf":
        raise ValueError("El destino debe terminar en .pdf.")
    if ruta.exists():
        # No sobrescribir una entrega previa: crear nombre consecutivo.
        n=2
        while ruta.with_name(f"{ruta.stem}_{n}.pdf").exists():
            n+=1
        ruta=ruta.with_name(f"{ruta.stem}_{n}.pdf")
    def pie(canvas, doc):
        canvas.setFont("LabSans",8)
        canvas.setFillColor(colors.HexColor("#56657a"))
        canvas.drawRightString(A4[0]-42,25,f"Página {doc.page}")
    SimpleDocTemplate(str(ruta),pagesize=A4,rightMargin=42,leftMargin=42,topMargin=38,
                      bottomMargin=40,title="Skill Lab 3 - Evidencia de aprendizaje").build(
                          elementos,onFirstPage=pie,onLaterPages=pie)
    return ruta
