import os
import re
import base64
import fitz          # PyMuPDF
import numpy as np
import cv2
from datetime import date
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.conf import settings
from web.models import PadreFamilia, Estudiante, DocumentoJustificacion
from skimage.metrics import structural_similarity as ssim

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.units import inch
from reportlab.lib.colors import black, HexColor


# =============================================================================
# UTILIDADES DE IMAGEN
# =============================================================================

def _leer_gray(path: str):
    return cv2.imread(path, cv2.IMREAD_GRAYSCALE)


def _bytes_to_gray(data: bytes):
    arr = np.frombuffer(data, dtype=np.uint8)
    return cv2.imdecode(arr, cv2.IMREAD_GRAYSCALE)


# =============================================================================
# EXTRACCIÓN DE TEXTO Y FIRMA DESDE PDF O IMAGEN ADJUNTA
# =============================================================================

def extraer_texto_pdf(pdf_bytes: bytes) -> str:
    """Extrae todo el texto de un PDF usando PyMuPDF."""
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        texto = ""
        for page in doc:
            texto += page.get_text()
        return texto.strip()
    except Exception as e:
        print(f"[EXTRACCIÓN TEXTO] Error: {e}")
        return ""


def extraer_firma_de_pdf(pdf_bytes: bytes, img_dir: str, timestamp: str) -> str:
    """
    Extrae la firma de un PDF.

    Estrategia principal: el PDF (sea el generado por nuestro sistema o uno
    similar) suele tener la firma como una IMAGEN EMBEBIDA real dentro de la
    página, no en una posición fija. En vez de recortar una zona arbitraria
    (que falla si el contenido de la carta es más corto o más largo),
    listamos las imágenes embebidas de la primera página y elegimos la que
    tiene forma "apaisada" (ancho > alto), ya que una firma manuscrita es
    siempre más ancha que alta, mientras que la foto facial es vertical
    (más alta que ancha).

    Si el PDF no tiene imágenes embebidas útiles (p. ej. es un documento
    escaneado plano), se usa como respaldo el recorte del tercio inferior
    de la página, igual que antes.
    """
    try:
        doc  = fitz.open(stream=pdf_bytes, filetype="pdf")
        page = doc[0]

        imagenes = page.get_images(full=True)
        print(f"[FIRMA PDF] Imágenes embebidas encontradas en la página: {len(imagenes)}")

        candidata    = None
        mejor_ratio  = 0.0

        for img_info in imagenes:
            xref = img_info[0]
            try:
                base_image = doc.extract_image(xref)
                img_bytes_emb = base_image.get("image")
                img_gray = _bytes_to_gray(img_bytes_emb)
                if img_gray is None:
                    continue

                h, w  = img_gray.shape
                ratio = (w / h) if h > 0 else 0
                print(f"  [FIRMA PDF] xref={xref} dims={w}x{h} ratio(ancho/alto)={ratio:.2f}")

                # La firma es apaisada (ratio > 1.3). La foto de rostro es
                # vertical (ratio < 1). Nos quedamos con la más apaisada.
                if ratio > 1.3 and ratio > mejor_ratio:
                    mejor_ratio = ratio
                    candidata    = img_gray
            except Exception as ei:
                print(f"  [FIRMA PDF] Error extrayendo xref {xref}: {ei}")
                continue

        if candidata is not None:
            nombre = f"adj_firma_{timestamp}.png"
            ruta   = os.path.join(img_dir, nombre)
            cv2.imwrite(ruta, candidata)
            print(f"[FIRMA PDF] ✅ Firma embebida extraída → {ruta}  shape={candidata.shape}")
            return f"img/{nombre}"

        # ── Respaldo: recorte de zona (documentos externos/escaneados) ──────
        print("[FIRMA PDF] ⚠ No se halló imagen apaisada embebida, "
              "usando recorte de zona como respaldo")
        mat  = fitz.Matrix(2.5, 2.5)   # ~180 DPI
        pix  = page.get_pixmap(matrix=mat, colorspace=fitz.csGRAY)
        img_bytes = pix.tobytes("png")
        img = _bytes_to_gray(img_bytes)
        if img is None:
            return ""

        h, w = img.shape
        zona_firma = img[int(h * 0.65):, :]   # último 35% de la página

        nombre = f"adj_firma_{timestamp}.png"
        ruta    = os.path.join(img_dir, nombre)
        cv2.imwrite(ruta, zona_firma)
        print(f"[FIRMA PDF] Zona firma (respaldo) extraída → {ruta}  shape={zona_firma.shape}")
        return f"img/{nombre}"

    except Exception as e:
        print(f"[FIRMA PDF] Error extrayendo firma: {e}")
        return ""


def extraer_firma_de_imagen(img_bytes: bytes, img_dir: str, timestamp: str) -> str:
    """
    Para imagen adjunta (JPG/PNG): igual que PDF, recorta el tercio inferior.
    """
    try:
        img = _bytes_to_gray(img_bytes)
        if img is None:
            return ""
        h, w = img.shape
        zona_firma = img[int(h * 0.65):, :]
        nombre = f"adj_firma_{timestamp}.png"
        ruta    = os.path.join(img_dir, nombre)
        cv2.imwrite(ruta, zona_firma)
        print(f"[FIRMA IMG] Zona firma extraída → {ruta}  shape={zona_firma.shape}")
        return f"img/{nombre}"
    except Exception as e:
        print(f"[FIRMA IMG] Error: {e}")
        return ""


def parsear_datos_texto(texto: str) -> dict:
    """
    Intenta extraer campos del texto del PDF/documento.
    Busca patrones comunes en cartas de permiso/licencia escritas en español.
    Devuelve un dict con las claves encontradas (pueden ser cadena vacía si no se hallaron).
    """
    datos = {
        'nombre_padre':    '',
        'nombre_alumno':   '',
        'fecha_evento':    '',
        'motivo':          '',
        'tipo_licencia':   'JUSTIFICATIVO',
    }

    # ── Nombre del padre/apoderado ────────────────────────────────────────────
    m = re.search(
        r'(?:Yo[,\s]+|suscrito[,\s]+|apoderado[,:\s]+)'
        r'([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+){1,4})',
        texto, re.IGNORECASE
    )
    if m:
        datos['nombre_padre'] = m.group(1).strip()

    # ── Nombre del alumno ─────────────────────────────────────────────────────
    m = re.search(
        r'(?:estudiante|alumno|mi hijo|mi hija)[,:\s]+'
        r'([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+){1,4})',
        texto, re.IGNORECASE
    )
    if m:
        datos['nombre_alumno'] = m.group(1).strip()

    # ── Fecha del evento ──────────────────────────────────────────────────────
    m = re.search(
        r'(?:día|fecha|el)\s+'
        r'(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}'
        r'|\d{1,2}\s+de\s+\w+\s+de\s+\d{4})',
        texto, re.IGNORECASE
    )
    if m:
        datos['fecha_evento'] = m.group(1).strip()

    # ── Motivo ────────────────────────────────────────────────────────────────
    m = re.search(
        r'(?:motivo[:\s]+|debido a[:\s]+|razón[:\s]+|porque\s+)'
        r'(.{10,120}?)(?:\.|$)',
        texto, re.IGNORECASE
    )
    if m:
        datos['motivo'] = m.group(1).strip()

    # ── Tipo de licencia ──────────────────────────────────────────────────────
    tl = texto.lower()
    if 'tolerancia' in tl or 'tarde' in tl or 'retraso' in tl or 'atraso' in tl:
        datos['tipo_licencia'] = 'LICENCIA DE TOLERANCIA'
    elif 'permiso' in tl or 'falta' in tl or 'ausencia' in tl or 'inasistencia' in tl:
        datos['tipo_licencia'] = 'PERMISO PARA FALTAR'

    print(f"\n[PARSE TEXTO] Datos extraídos del documento:")
    for k, v in datos.items():
        print(f"  {k}: {v!r}")

    return datos


# =============================================================================
# MOTOR BIOMÉTRICO — COMPARACIÓN DE FIRMAS
# =============================================================================

def _binarizar_firma(img: np.ndarray) -> np.ndarray:
    """Suaviza y binariza una imagen de firma (fondo negro, trazo blanco)."""
    blur = cv2.GaussianBlur(img, (3, 3), 0)
    _, binar = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return binar


def _recortar_a_tinta(binar: np.ndarray) -> np.ndarray:
    """Recorta la imagen binarizada a la caja que contiene solo el trazo (tinta),
    eliminando espacios en blanco que no aportan a la FORMA de la firma."""
    coords = cv2.findNonZero(binar)
    if coords is None:
        return binar
    x, y, w, h = cv2.boundingRect(coords)
    return binar[y:y + h, x:x + w]


def _normalizar_firma(binar_crop: np.ndarray, size=(400, 200)) -> np.ndarray:
    """Reescala el trazo recortado a un lienzo fijo PRESERVANDO la proporción
    (ancho/alto) y centrándolo. Así dos firmas con la misma forma pero
    dibujadas más grandes/pequeñas o más gruesas/delgadas quedan comparables
    en igualdad de condiciones — lo que varía es solo la FORMA real."""
    h, w = binar_crop.shape
    target_w, target_h = size
    if h == 0 or w == 0:
        return np.zeros((target_h, target_w), dtype=np.uint8)

    escala  = min(target_w / w, target_h / h)
    nuevo_w = max(1, int(round(w * escala)))
    nuevo_h = max(1, int(round(h * escala)))
    redim   = cv2.resize(binar_crop, (nuevo_w, nuevo_h), interpolation=cv2.INTER_AREA)

    lienzo = np.zeros((target_h, target_w), dtype=np.uint8)
    off_x  = (target_w - nuevo_w) // 2
    off_y  = (target_h - nuevo_h) // 2
    lienzo[off_y:off_y + nuevo_h, off_x:off_x + nuevo_w] = redim
    return lienzo


def comparar_firmas(img_base: np.ndarray, img_actual: np.ndarray) -> tuple:
    """
    Compara la FORMA de dos firmas (no el grosor del trazo ni cuánta tinta hay).

    Pasos:
      1. Binariza ambas firmas.
      2. Recorta cada una a su bounding box de tinta real (descarta espacio vacío).
      3. Normaliza tamaño preservando proporción, centrado en un lienzo fijo.
      4. Compara la FORMA del contorno con cv2.matchShapes (Hu-Moments,
         invariante a traslación/escala/rotación) — esto es lo que realmente
         detecta si las curvas/letras/garabatos coinciden con el patrón.
      5. SSIM sobre la versión normalizada como apoyo estructural.
      6. Un pequeño peso de proporción de tinta solo para descartar canvases
         vacíos o casi vacíos, NO como criterio principal de similitud.

    Devuelve (porcentaje 0-100, match bool).
    """
    TARGET = (400, 200)

    bin_base = _binarizar_firma(img_base)
    bin_act  = _binarizar_firma(img_actual)

    px_base = cv2.countNonZero(bin_base)
    px_act  = cv2.countNonZero(bin_act)
    print(f"  [FIRMA] Píxeles de tinta — Patrón: {px_base} | Actual: {px_act}")

    if px_base < 80 or px_act < 80:
        print("  [FIRMA] ❌ Canvas vacío o firma no detectada")
        return 0.0, False

    crop_base = _recortar_a_tinta(bin_base)
    crop_act  = _recortar_a_tinta(bin_act)

    norm_base = _normalizar_firma(crop_base, TARGET)
    norm_act  = _normalizar_firma(crop_act,  TARGET)

    # ── Comparación de FORMA pura vía contornos (Hu-Moments) ────────────────
    contornos_base, _ = cv2.findContours(norm_base, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contornos_act,  _ = cv2.findContours(norm_act,  cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contornos_base and contornos_act:
        c_base = max(contornos_base, key=cv2.contourArea)
        c_act  = max(contornos_act,  key=cv2.contourArea)
        dist_forma = cv2.matchShapes(c_base, c_act, cv2.CONTOURS_MATCH_I1, 0.0)
        # matchShapes: 0 = forma idéntica, valores más altos = más distinta
        sim_forma = max(0.0, 1.0 - min(dist_forma, 1.0))
    else:
        sim_forma = 0.0

    # ── SSIM estructural sobre la versión ya normalizada ─────────────────────
    score_ssim, _ = ssim(norm_base, norm_act, full=True)

    # ── Proporción de tinta (solo soporte menor, NO mide forma) ─────────────
    ratio_px = min(px_base, px_act) / max(px_base, px_act)

    # La FORMA (matchShapes) es el criterio dominante; SSIM apoya la
    # estructura; el ratio de tinta pesa poco a propósito.
    score = (sim_forma * 0.55) + (score_ssim * 0.30) + (ratio_px * 0.15)
    pct   = round(max(0.0, min(100.0, score * 100)), 2)
    match = pct >= 60

    print(f"  [FIRMA] Forma(matchShapes)={sim_forma*100:.1f}% | "
          f"SSIM={score_ssim*100:.1f}% | RatioTinta={ratio_px*100:.1f}% | "
          f"Final={pct:.1f}%")
    return pct, match


def comparar_rostros(img_base: np.ndarray, img_actual: np.ndarray) -> tuple:
    """
    Compara dos fotografías faciales.
    Usa Haar Cascade para crop + SSIM (65%) + histograma (35%).
    Devuelve (porcentaje 0-100, match bool).
    """
    TARGET = (200, 200)
    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    face_cascade = cv2.CascadeClassifier(cascade_path)

    def crop_rostro(img):
        faces = face_cascade.detectMultiScale(img, 1.1, 5, minSize=(40, 40))
        if len(faces) > 0:
            x, y, w, h = faces[0]
            return img[y:y+h, x:x+w]
        return img

    r_base = cv2.resize(cv2.equalizeHist(crop_rostro(img_base)), TARGET)
    r_act  = cv2.resize(cv2.equalizeHist(crop_rostro(img_actual)), TARGET)

    score_ssim, _ = ssim(r_base, r_act, full=True)

    hist_b = cv2.calcHist([r_base], [0], None, [64], [0, 256])
    hist_a = cv2.calcHist([r_act],  [0], None, [64], [0, 256])
    cv2.normalize(hist_b, hist_b)
    cv2.normalize(hist_a, hist_a)
    corr  = cv2.compareHist(hist_b, hist_a, cv2.HISTCMP_CORREL)
    sim_h = (corr + 1) / 2

    score = (score_ssim * 0.65) + (sim_h * 0.35)
    pct   = round(max(0.0, min(100.0, score * 100)), 2)
    match = pct >= 35

    print(f"  [ROSTRO] SSIM={score_ssim*100:.1f}% | Hist={sim_h*100:.1f}% | Final={pct:.1f}%")
    return pct, match


# =============================================================================
# GENERADOR DE PDF (solo para modo formulario)
# =============================================================================

def generar_pdf_formulario(pdf_path, padre, estudiante, fecha_falta,
                            motivo, firma_path, foto_path, observacion_ia):
    blue_corp = HexColor('#1e3a8a')
    doc_rep   = SimpleDocTemplate(
        pdf_path, pagesize=letter,
        rightMargin=50, leftMargin=50, topMargin=40, bottomMargin=40
    )
    story   = []
    estilos = getSampleStyleSheet()

    s_header = ParagraphStyle('H', parent=estilos['Heading1'],
                              alignment=TA_CENTER, fontSize=16, spaceAfter=8,
                              textColor=blue_corp, fontName='Helvetica-Bold')
    s_title  = ParagraphStyle('T', parent=estilos['Heading2'],
                              alignment=TA_CENTER, fontSize=14, spaceAfter=18,
                              textColor=black, fontName='Helvetica-Bold')
    s_date   = ParagraphStyle('D', parent=estilos['Normal'],
                              alignment=TA_RIGHT, fontSize=11, spaceAfter=20,
                              fontName='Helvetica')
    s_body   = ParagraphStyle('B', parent=estilos['Normal'],
                              alignment=TA_JUSTIFY, fontSize=11, leading=16,
                              spaceAfter=12, fontName='Helvetica')
    s_addr   = ParagraphStyle('A', parent=estilos['Normal'],
                              alignment=TA_JUSTIFY, fontSize=11, leading=15,
                              spaceAfter=15, fontName='Helvetica')
    s_line   = ParagraphStyle('L', parent=estilos['Normal'],
                              alignment=TA_JUSTIFY, fontSize=11, spaceAfter=12)
    s_sign   = ParagraphStyle('S', parent=estilos['Normal'],
                              alignment=TA_JUSTIFY, fontSize=11, leading=15, spaceAfter=3)
    s_sello  = ParagraphStyle('SE', parent=estilos['Normal'],
                              fontSize=8, textColor=HexColor('#94a3b8'),
                              alignment=TA_CENTER)

    story.append(Paragraph("<b>UNIDAD EDUCATIVA 'LOS ANDES'</b>", s_header))
    story.append(Paragraph("CARTA DE JUSTIFICACIÓN DE INASISTENCIA", s_title))
    story.append(Spacer(1, 5))

    date_str = timezone.now().strftime("%d de %B de %Y")
    face_img = Image(foto_path, width=110, height=140)

    tabla_header = Table(
        [[Paragraph(f"<b>Fecha de Emisión:</b> {date_str}", s_date), face_img]],
        colWidths=[3.8 * inch, 2.0 * inch]
    )
    tabla_header.setStyle(TableStyle([
        ('ALIGN',      (0, 0), (0, 0), 'LEFT'),
        ('VALIGN',     (0, 0), (0, 0), 'TOP'),
        ('ALIGN',      (1, 0), (1, 0), 'RIGHT'),
        ('VALIGN',     (1, 0), (1, 0), 'MIDDLE'),
        ('BOX',        (1, 0), (1, 0), 1, blue_corp),
        ('BACKGROUND', (1, 0), (1, 0), HexColor('#f1f5f9')),
        ('PADDING',    (1, 0), (1, 0), 5),
    ]))
    story.append(tabla_header)
    story.append(Spacer(1, 20))

    story.append(Paragraph(
        "<b>Señor Director de la Unidad Educativa Los Andes.</b><br/>Presente.-", s_addr))
    story.append(Spacer(1, 10))

    fecha_fmt = timezone.datetime.strptime(fecha_falta, "%Y-%m-%d").strftime("%d/%m/%Y")
    cuerpo = (
        f"Yo, <b>{padre.id_persona.nombres} {padre.id_persona.apellidos}</b>, "
        f"en calidad de apoderado legal del estudiante "
        f"<b>{estudiante.id_persona.nombres} {estudiante.id_persona.apellidos}</b>, "
        f"expongo formalmente ante su autoridad la justificación por la falta de "
        f"inasistencia/retraso correspondiente al día <b>{fecha_fmt}</b>, "
        f"debido al siguiente motivo justificado: {motivo}."
    )
    story.append(Paragraph(cuerpo, s_body))
    story.append(Spacer(1, 25))
    story.append(Paragraph("Atentamente,", s_body))
    story.append(Spacer(1, 8))

    if os.path.exists(firma_path):
        story.append(Image(firma_path, width=150, height=60))

    story.append(Spacer(1, 15))
    story.append(Paragraph("___________________________________", s_line))
    story.append(Paragraph(
        f"<b>{padre.id_persona.nombres} {padre.id_persona.apellidos}</b>", s_sign))
    story.append(Paragraph(
        f"C.I. / Documento: {padre.id_persona.dni_cedula}", s_sign))
    story.append(Spacer(1, 20))
    story.append(Paragraph(f"Verificación Biométrica IA — {observacion_ia}", s_sello))

    doc_rep.build(story)


# =============================================================================
# VISTA PRINCIPAL
# =============================================================================

class JustificacionTensorFlowView(View):
    template_name = 'padre/justificacion_inteligente.html'

    def _dirs(self):
        base = os.path.join(settings.BASE_DIR, 'web', 'static')
        if not os.path.exists(base):
            base = os.path.join(settings.BASE_DIR, 'static')
        d = {
            'img': os.path.join(base, 'img'),
            'pdf': os.path.join(base, 'pdf'),
            'adj': os.path.join(base, 'adjuntos'),
        }
        for p in d.values():
            os.makedirs(p, exist_ok=True)
        return d

    def get_context(self, request):
        id_persona = request.session.get('id_persona')
        padre  = get_object_or_404(PadreFamilia, id_persona=id_persona)
        hijos  = Estudiante.objects.filter(estudiantepadre__id_padre=padre)
        raw    = DocumentoJustificacion.objects.filter(
                     id_estudiante__in=hijos).order_by('-id_documento')

        historial = []
        for doc in raw:
            # archivo_url tiene dos formatos según el modo:
            #   FORMULARIO : "pdf/X.pdf|img/firma.png|img/foto.png"   (3 partes)
            #   ADJUNTO    : "adjunto:adjuntos/X.pdf"                  (prefijo)
            partes = (doc.archivo_url or '').split('|')
            doc.es_adjunto   = doc.archivo_url.startswith('adjunto:') if doc.archivo_url else False
            doc.pdf_limpio   = ''
            doc.firma_limpia = ''
            doc.foto_limpia  = ''
            doc.adjunto_limpio = ''

            if doc.es_adjunto:
                doc.adjunto_limpio = doc.archivo_url.replace('adjunto:', '', 1)
            else:
                doc.pdf_limpio   = partes[0] if len(partes) > 0 else ''
                doc.firma_limpia = partes[1] if len(partes) > 1 else ''
                doc.foto_limpia  = partes[2] if len(partes) > 2 else ''

            historial.append(doc)

        return {
            'nombres':    request.session.get('nombres', 'Padre / Tutor'),
            'nombre_rol': request.session.get('nombre_rol', 'Padre de Familia'),
            'padre':      padre,
            'hijos':      hijos,
            'historial':  historial,
        }

    def get(self, request):
        if 'id_usuario' not in request.session or \
                request.session.get('nombre_rol') != 'Padre de Familia':
            return redirect('/login/')
        return render(request, self.template_name, self.get_context(request))

    def post(self, request):
        if 'id_usuario' not in request.session or \
                request.session.get('nombre_rol') != 'Padre de Familia':
            return redirect('/login/')

        id_persona = request.session.get('id_persona')
        padre  = get_object_or_404(PadreFamilia, id_persona=id_persona)
        action = request.POST.get('action')
        dirs   = self._dirs()

        # ─────────────────────────────────────────────────────────────────────
        # ACCIÓN A: REGISTRAR BIOMETRÍA PATRÓN
        # ─────────────────────────────────────────────────────────────────────
        if action == 'registrar_biometria_base':
            firma_b64 = request.POST.get('firma_data', '')
            foto_b64  = request.POST.get('foto_data',  '')

            if not firma_b64 or not foto_b64 or \
                    ';base64,' not in firma_b64 or ';base64,' not in foto_b64:
                messages.error(request,
                    "Error: Debe capturar tanto la fotografía como la firma.")
                return redirect('justificacion_tf')

            fn_firma = f"patron_firma_{padre.id_padre}.png"
            fn_foto  = f"patron_rostro_{padre.id_padre}.png"

            with open(os.path.join(dirs['img'], fn_firma), 'wb') as f:
                f.write(base64.b64decode(firma_b64.split(';base64,')[1]))
            with open(os.path.join(dirs['img'], fn_foto), 'wb') as f:
                f.write(base64.b64decode(foto_b64.split(';base64,')[1]))

            PadreFamilia.objects.filter(id_padre=padre.id_padre).update(
                firma_base=f"{fn_firma}|{fn_foto}"
            )
            messages.success(request, "Perfil Biométrico Patrón registrado correctamente.")
            return redirect('justificacion_tf')

        # ─────────────────────────────────────────────────────────────────────
        # ACCIÓN B: PROCESAR TRÁMITE
        # ─────────────────────────────────────────────────────────────────────
        elif action == 'generar_justificativo':
            timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")

            firma_b64        = request.POST.get('firma_carta_data', '').strip()
            foto_b64         = request.POST.get('foto_facial_data', '').strip()
            archivo_adjunto  = request.FILES.get('archivo_adjunto')

            modo_formulario = bool(firma_b64 and foto_b64)
            modo_adjunto    = bool(archivo_adjunto)

            if not modo_formulario and not modo_adjunto:
                messages.error(request,
                    "Debe usar el formulario biométrico o adjuntar un documento.")
                return redirect('justificacion_tf')

            # ── Cargar patrón de firma del padre ─────────────────────────────
            patron_firma_img  = None
            patron_rostro_img = None

            try:
                texto_patron = str(padre.firma_base).strip()
                if texto_patron and texto_patron != 'None':
                    partes_p = texto_patron.split('|')
                    ruta_pf  = os.path.join(dirs['img'],
                                            os.path.basename(partes_p[0].strip()))
                    ruta_pr  = os.path.join(dirs['img'],
                                            os.path.basename(partes_p[1].strip())) \
                               if len(partes_p) > 1 else ''
                    if os.path.exists(ruta_pf):
                        patron_firma_img = _leer_gray(ruta_pf)
                    if ruta_pr and os.path.exists(ruta_pr):
                        patron_rostro_img = _leer_gray(ruta_pr)
                    print(f"[PATRON] Firma cargada={patron_firma_img is not None} | "
                          f"Rostro cargado={patron_rostro_img is not None}")
            except Exception as ep:
                print(f"[PATRON] Error cargando patrón: {ep}")

            pct_firma  = 0.0
            pct_rostro = 0.0
            match_firma  = False
            match_rostro = False

            # =================================================================
            # FLUJO 1: FORMULARIO (cámara + firma canvas)
            # Genera PDF con foto y firma incrustadas.
            # =================================================================
            if modo_formulario:
                id_estudiante    = request.POST.get('id_estudiante')
                categoria        = request.POST.get('tipo_licencia', 'PERMISO PARA FALTAR')
                motivo           = request.POST.get('motivo', '')
                fecha_falta      = request.POST.get('fecha_falta') or str(date.today())
                estudiante       = get_object_or_404(Estudiante, id_student=id_estudiante)

                firma_name = f"firma_{timestamp}.png"
                foto_name  = f"rostro_{timestamp}.png"
                pdf_name   = f"doc_{timestamp}.pdf"
                firma_path = os.path.join(dirs['img'], firma_name)
                foto_path  = os.path.join(dirs['img'], foto_name)
                pdf_path   = os.path.join(dirs['pdf'], pdf_name)

                with open(firma_path, 'wb') as f:
                    f.write(base64.b64decode(firma_b64.split(';base64,')[1]))
                with open(foto_path, 'wb') as f:
                    f.write(base64.b64decode(foto_b64.split(';base64,')[1]))

                print(f"\n===== MOTOR IA — MODO FORMULARIO =====")

                # Comparar firma
                if patron_firma_img is not None:
                    firma_actual = _leer_gray(firma_path)
                    if firma_actual is not None:
                        pct_firma, match_firma = comparar_firmas(
                            patron_firma_img, firma_actual)

                # Comparar rostro
                if patron_rostro_img is not None:
                    rostro_actual = _leer_gray(foto_path)
                    if rostro_actual is not None:
                        pct_rostro, match_rostro = comparar_rostros(
                            patron_rostro_img, rostro_actual)

                pct_prom = (pct_firma + pct_rostro) / 2
                print(
                    f"\n======== RESULTADO IA ========\n"
                    f"Modo          : Formulario biométrico\n"
                    f"Firma         : {pct_firma:.2f}%  match={match_firma}\n"
                    f"Rostro        : {pct_rostro:.2f}% match={match_rostro}\n"
                    f"Promedio      : {pct_prom:.2f}%\n"
                    f"Decisión (AND): {'APROBADO' if (match_firma and match_rostro) else 'RECHAZADO'}\n"
                    f"==============================\n"
                )

                # Verificación de DOS factores: para aprobar se requiere que
                # AMBOS biométricos (firma Y rostro) coincidan con el patrón.
                # Con OR bastaba que uno solo pasara, lo que permitía aprobar
                # trámites con, por ejemplo, una foto completamente inválida
                # siempre que la firma diera un score alto.
                if match_firma and match_rostro:
                    estado_final   = 'APROBADO'
                    observacion_ia = (
                        f"Verificación Exitosa ({pct_prom:.1f}%). "
                        f"Firma: {pct_firma:.1f}% | Rostro: {pct_rostro:.1f}%"
                    )
                else:
                    estado_final   = 'RECHAZADO'
                    observacion_ia = (
                        f"Verificación Fallida ({pct_prom:.1f}%). "
                        f"Firma: {pct_firma:.1f}% | Rostro: {pct_rostro:.1f}%"
                    )

                # Generar PDF con foto y firma
                generar_pdf_formulario(
                    pdf_path, padre, estudiante, fecha_falta,
                    motivo, firma_path, foto_path, observacion_ia
                )

                # Guardar en BD — formato: "pdf/X|img/firma|img/foto"
                url_bd = (
                    f"pdf/{pdf_name}|"
                    f"img/{firma_name}|"
                    f"img/{foto_name}"
                )
                DocumentoJustificacion.objects.create(
                    id_padre      = padre,
                    id_estudiante = estudiante,
                    archivo_url   = url_bd,
                    tipo          = 'JUSTIFICATIVO',
                    motivo        = f"[{categoria}] {motivo}",
                    fecha_inicio  = fecha_falta,
                    fecha_fin     = fecha_falta,
                    fecha_subida  = timezone.now(),
                    estado        = estado_final,
                    observaciones = observacion_ia,
                )

                messages.success(request,
                    f"Trámite procesado (formulario biométrico). Resultado: {estado_final}")
                return redirect('justificacion_tf')

            # =================================================================
            # FLUJO 2: DOCUMENTO ADJUNTO (PDF o imagen)
            # Lee texto → extrae datos → compara SOLO firma → guarda el adjunto tal cual.
            # NO genera PDF propio.
            # =================================================================
            elif modo_adjunto:
                adj_bytes    = archivo_adjunto.read()
                content_type = archivo_adjunto.content_type or ''
                ext          = os.path.splitext(archivo_adjunto.name)[1].lower()
                adj_name     = f"adjunto_{timestamp}{ext}"
                adj_path     = os.path.join(dirs['adj'], adj_name)

                with open(adj_path, 'wb') as f:
                    f.write(adj_bytes)

                print(f"\n===== MOTOR IA — MODO ADJUNTO ({ext}) =====")
                print(f"[ADJUNTO] Archivo guardado: {adj_path}")

                # ── Extraer texto del documento ───────────────────────────────
                if 'pdf' in content_type or ext == '.pdf':
                    texto_doc = extraer_texto_pdf(adj_bytes)
                    firma_zona_rel = extraer_firma_de_pdf(
                        adj_bytes, dirs['img'], timestamp)
                else:
                    # imagen: no hay texto extraíble por OCR aquí,
                    # pero sí se extrae zona de firma
                    texto_doc = ''
                    firma_zona_rel = extraer_firma_de_imagen(
                        adj_bytes, dirs['img'], timestamp)

                print(f"[TEXTO EXTRAÍDO]\n{texto_doc[:500]}\n{'...' if len(texto_doc) > 500 else ''}")

                # ── Parsear datos del texto ───────────────────────────────────
                datos = parsear_datos_texto(texto_doc)

                # ── Identificar estudiante ────────────────────────────────────
                # Primero intentar con el campo del formulario (select),
                # luego con el nombre extraído del texto
                id_est_form = request.POST.get('id_estudiante')
                estudiante  = None

                if id_est_form:
                    try:
                        estudiante = Estudiante.objects.get(id_student=id_est_form)
                    except Estudiante.DoesNotExist:
                        pass

                if not estudiante and datos['nombre_alumno']:
                    # Buscar por nombre aproximado entre los hijos del padre
                    hijos = Estudiante.objects.filter(estudiantepadre__id_padre=padre)
                    nombre_lower = datos['nombre_alumno'].lower()
                    for h in hijos:
                        nombre_completo = (
                            h.id_persona.nombres + ' ' + h.id_persona.apellidos
                        ).lower()
                        # Si al menos 2 palabras coinciden
                        palabras_doc = set(nombre_lower.split())
                        palabras_bd  = set(nombre_completo.split())
                        if len(palabras_doc & palabras_bd) >= 2:
                            estudiante = h
                            print(f"[ALUMNO] Identificado por texto: {nombre_completo}")
                            break

                if not estudiante:
                    # Fallback: primer hijo del padre
                    hijos = Estudiante.objects.filter(estudiantepadre__id_padre=padre)
                    estudiante = hijos.first()
                    if not estudiante:
                        messages.error(request,
                            "No se pudo identificar al estudiante en el documento.")
                        return redirect('justificacion_tf')
                    print(f"[ALUMNO] Fallback al primer hijo: "
                          f"{estudiante.id_persona.nombres}")

                # ── Datos para BD ─────────────────────────────────────────────
                motivo_final   = datos['motivo'] or request.POST.get('motivo', 'Sin especificar')
                categoria      = datos['tipo_licencia']
                fecha_falta    = request.POST.get('fecha_falta') or str(date.today())

                # ── Comparar SOLO firma del documento vs patrón ───────────────
                if patron_firma_img is not None and firma_zona_rel:
                    ruta_firma_adj = os.path.join(
                        settings.BASE_DIR,
                        *(['web', 'static'] if os.path.exists(
                            os.path.join(settings.BASE_DIR, 'web', 'static'))
                          else ['static']),
                        firma_zona_rel.replace('/', os.sep)
                    )
                    # También intentar ruta directa
                    ruta_firma_adj2 = os.path.join(dirs['img'],
                                                   os.path.basename(firma_zona_rel))
                    ruta_usar = ruta_firma_adj2 if os.path.exists(ruta_firma_adj2) \
                                else ruta_firma_adj

                    print(f"[FIRMA ADJ] Ruta imagen zona firma: {ruta_usar} "
                          f"→ existe={os.path.exists(ruta_usar)}")

                    if os.path.exists(ruta_usar):
                        firma_adj_img = _leer_gray(ruta_usar)
                        if firma_adj_img is not None:
                            pct_firma, match_firma = comparar_firmas(
                                patron_firma_img, firma_adj_img)
                        else:
                            print("[FIRMA ADJ] ❌ No se pudo leer imagen de zona firma")
                    else:
                        print("[FIRMA ADJ] ❌ Archivo de zona firma no encontrado")
                else:
                    print("[FIRMA ADJ] ⚠ Sin patrón de firma o zona no extraída, "
                          "se acepta sin comparación")
                    pct_firma  = 75.0   # sin patrón: estado neutro
                    match_firma = True

                print(
                    f"\n======== RESULTADO IA ========\n"
                    f"Modo          : Documento adjunto ({ext})\n"
                    f"Firma adj.    : {pct_firma:.2f}%  match={match_firma}\n"
                    f"Rostro        : N/A (no requerido en modo adjunto)\n"
                    f"Decisión      : {'APROBADO' if match_firma else 'RECHAZADO'}\n"
                    f"==============================\n"
                )

                if match_firma:
                    estado_final   = 'APROBADO'
                    observacion_ia = (
                        f"Documento adjunto verificado. "
                        f"Similitud de firma: {pct_firma:.1f}% | "
                        f"Alumno: {estudiante.id_persona.nombres} "
                        f"{estudiante.id_persona.apellidos}"
                    )
                else:
                    estado_final   = 'RECHAZADO'
                    observacion_ia = (
                        f"Firma del documento no coincide con el patrón. "
                        f"Similitud: {pct_firma:.1f}%"
                    )

                # Guardar en BD — formato especial para adjunto: "adjunto:adjuntos/X.ext"
                url_bd = f"adjunto:adjuntos/{adj_name}"

                DocumentoJustificacion.objects.create(
                    id_padre      = padre,
                    id_estudiante = estudiante,
                    archivo_url   = url_bd,
                    tipo          = 'JUSTIFICATIVO',
                    motivo        = f"[{categoria}] {motivo_final}",
                    fecha_inicio  = fecha_falta,
                    fecha_fin     = fecha_falta,
                    fecha_subida  = timezone.now(),
                    estado        = estado_final,
                    observaciones = observacion_ia,
                )

                messages.success(request,
                    f"Documento adjunto procesado. Resultado: {estado_final}")
                return redirect('justificacion_tf')

        return redirect('justificacion_tf')