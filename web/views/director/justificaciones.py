import json

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.http import JsonResponse
from django.utils import timezone

from web.models import DocumentoJustificacion, Estudiante, PadreFamilia


# =============================================================================
# UTILIDAD COMPARTIDA: separar archivo_url en sus componentes
# =============================================================================
def _descomponer_archivo_url(doc):
    """
    archivo_url tiene dos formatos según el modo en que se generó:
      FORMULARIO : "pdf/X.pdf|img/firma.png|img/foto.png"   (3 partes)
      ADJUNTO    : "adjunto:adjuntos/X.pdf"                  (prefijo)
    Adjunta los atributos limpios directamente al objeto doc para usarlos
    cómodamente en el template.
    """
    archivo_url = doc.archivo_url or ''
    doc.es_adjunto     = archivo_url.startswith('adjunto:')
    doc.pdf_limpio     = ''
    doc.firma_limpia   = ''
    doc.foto_limpia    = ''
    doc.adjunto_limpio = ''

    if doc.es_adjunto:
        doc.adjunto_limpio = archivo_url.replace('adjunto:', '', 1)
    else:
        partes = archivo_url.split('|')
        doc.pdf_limpio   = partes[0] if len(partes) > 0 else ''
        doc.firma_limpia = partes[1] if len(partes) > 1 else ''
        doc.foto_limpia  = partes[2] if len(partes) > 2 else ''

    return doc


# =============================================================================
# VISTA PRINCIPAL: PANEL DEL DIRECTOR
# =============================================================================
class DirectorJustificacionesView(View):
    """
    Panel administrativo para que el Director:
      - Vea TODAS las justificaciones/licencias tramitadas por los padres.
      - Filtre por estado (PENDIENTE / APROBADO / RECHAZADO).
      - Vea el detalle completo (observación de la IA, % de firma/rostro,
        documentos adjuntos o generados).
      - Modifique manualmente el estado (override de la decisión de la IA),
        sin recargar la página (vía la API de abajo).
    """
    template_name = 'director/justificaciones_admin.html'

    def get(self, request):
        if 'id_usuario' not in request.session or \
                request.session.get('nombre_rol') != 'Director':
            return redirect('/login/')

        documentos_todos = DocumentoJustificacion.objects.select_related(
            'id_estudiante__id_persona',
            'id_padre__id_persona',
        ).order_by('-id_documento')

        # ── Conteos para las tarjetas de resumen (sobre el total, sin filtro) ──
        total           = documentos_todos.count()
        total_aprobados = documentos_todos.filter(estado='APROBADO').count()
        total_rechazados = documentos_todos.filter(estado='RECHAZADO').count()
        total_pendientes = documentos_todos.filter(estado='PENDIENTE').count()

        # ── Filtro opcional por estado (?estado=APROBADO) ───────────────────
        estado_filtro = request.GET.get('estado', '').upper().strip()
        documentos = documentos_todos
        if estado_filtro in ('APROBADO', 'RECHAZADO', 'PENDIENTE'):
            documentos = documentos.filter(estado=estado_filtro)

        historial = [_descomponer_archivo_url(doc) for doc in documentos]

        contexto = {
            'nombres':          request.session.get('nombres', 'Director'),
            'nombre_rol':       request.session.get('nombre_rol', 'Director'),
            'historial':        historial,
            'estado_filtro':    estado_filtro,
            'total':             total,
            'total_aprobados':   total_aprobados,
            'total_rechazados':  total_rechazados,
            'total_pendientes':  total_pendientes,
        }
        return render(request, self.template_name, contexto)


# =============================================================================
# API: ACTUALIZAR ESTADO (AJAX — sin recargar la página)
# =============================================================================
class ActualizarEstadoJustificacionAPI(View):
    """
    Permite al Director cambiar manualmente el estado de un documento
    (override de la decisión de la IA), vía fetch/AJAX desde el frontend.

    Espera JSON:
        {
            "id_documento": 12,
            "nuevo_estado": "APROBADO" | "RECHAZADO" | "PENDIENTE",
            "comentario": "texto opcional del director"
        }

    Devuelve JSON con el estado actualizado para que el frontend
    refresque la fila correspondiente sin recargar toda la página.
    """

    ESTADOS_VALIDOS = ('APROBADO', 'RECHAZADO', 'PENDIENTE')

    def post(self, request):
        if 'id_usuario' not in request.session or \
                request.session.get('nombre_rol') != 'Director':
            return JsonResponse({'ok': False, 'error': 'No autorizado.'}, status=403)

        try:
            data = json.loads(request.body.decode('utf-8'))
        except (ValueError, json.JSONDecodeError):
            return JsonResponse({'ok': False, 'error': 'JSON inválido.'}, status=400)

        id_documento  = data.get('id_documento')
        nuevo_estado  = str(data.get('nuevo_estado', '')).upper().strip()
        comentario    = str(data.get('comentario', '')).strip()

        if not id_documento or nuevo_estado not in self.ESTADOS_VALIDOS:
            return JsonResponse({'ok': False, 'error': 'Datos incompletos o estado inválido.'}, status=400)

        doc = get_object_or_404(DocumentoJustificacion, id_documento=id_documento)

        director_nombre = request.session.get('nombres', 'Director')
        sello_revision = (
            f"\n[Revisión manual del Director — {director_nombre} — "
            f"{timezone.now().strftime('%d/%m/%Y %H:%M')}] "
            f"Estado cambiado a {nuevo_estado}."
        )
        if comentario:
            sello_revision += f" Comentario: {comentario}"

        doc.estado = nuevo_estado
        doc.observaciones = (doc.observaciones or '') + sello_revision
        doc.save(update_fields=['estado', 'observaciones'])

        return JsonResponse({
            'ok':            True,
            'id_documento':  doc.id_documento,
            'estado':        doc.estado,
            'observaciones': doc.observaciones,
        })