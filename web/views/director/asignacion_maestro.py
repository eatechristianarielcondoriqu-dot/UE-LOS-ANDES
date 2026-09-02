from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from web.models import Gestion, Curso, Materia, Maestro, AsignacionDocente, CursoMateria

# ReportLab para la generación de PDFs
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

class AsignacionMaestroView(View):
    template_name = 'director/asignacion_maestro.html'

    def get_context(self, request):
        gestiones = Gestion.objects.all().order_by('-anio')
        cursos = Curso.objects.all().order_by('nombre', 'paralelo')
        maestros = Maestro.objects.select_related('id_persona').all()

        # Gestión activa
        gestion_id = request.GET.get('gestion_id') or request.session.get('malla_gestion_id')
        gestion_activa = None

        if gestion_id:
            gestion_activa = Gestion.objects.filter(id_gestion=gestion_id).first()
        if not gestion_activa:
            gestion_activa = Gestion.objects.filter(activa=True).first() or gestiones.first()

        if gestion_activa:
            request.session['malla_gestion_id'] = str(gestion_activa.id_gestion)

        # Construcción de la matriz estructurada por curso
        matriz_malla = []
        asignaciones = AsignacionDocente.objects.filter(id_gestion=gestion_activa)\
                                                .select_related('id_materia', 'id_maestro__id_persona')

        for curso in cursos:
            fila_docentes = []
            for asig in asignaciones:
                if asig.id_curso_id == curso.id_curso:
                    fila_docentes.append({
                        'id_asignacion': asig.id_asignacion,
                        'materia': asig.id_materia,
                        'maestro': asig.id_maestro
                    })
            
            matriz_malla.append({
                'curso': curso,
                'fila': fila_docentes
            })

        return {
           
            'nombres': request.session.get('nombres', 'Administrador'),
            'nombre_rol': request.session.get('nombre_rol', 'Director'),
            'gestiones': gestiones,
            'gestion_activa': gestion_activa,
            'cursos': cursos,
            'maestros': maestros,
            'matriz_malla': matriz_malla
        }

    def get(self, request):
        if 'id_usuario' not in request.session:
            return redirect('/login/')
        return render(request, self.template_name, self.get_context(request))

    def post(self, request):
        if 'id_usuario' not in request.session:
            return redirect('/login/')

        action = request.POST.get('action')

        if action == 'crear_asignacion':
            curso_id = request.POST.get('id_curso')
            materia_id = request.POST.get('id_materia')
            maestro_id = request.POST.get('id_maestro')
            gestion_id = request.session.get('malla_gestion_id')

            curso = get_object_or_404(Curso, id_curso=curso_id)
            materia = get_object_or_404(Materia, id_materia=materia_id)
            maestro = get_object_or_404(Maestro, id_maestro=maestro_id)
            gestion = get_object_or_404(Gestion, id_gestion=gestion_id)

            if AsignacionDocente.objects.filter(id_curso=curso, id_materia=materia, id_gestion=gestion).exists():
                messages.warning(request, "Esta materia ya tiene un docente asignado en este curso.")
            else:
                AsignacionDocente.objects.create(
                    id_curso=curso, id_materia=materia, id_maestro=maestro, id_gestion=gestion
                )
                messages.success(request, "Asignación docente registrada correctamente.")

        elif action == 'eliminar_asignacion':
            id_asig = request.POST.get('id_asignacion')
            get_object_or_404(AsignacionDocente, id_asignacion=id_asig).delete()
            messages.success(request, "Asignación removida correctamente.")

        return redirect('asignacion_maestros')


class AsignacionesFiltradasAPI(View):
    """API que devuelve las materias válidas para asignar según curso_materia y disponibilidad"""
    def get(self, request):
        curso_id = request.GET.get('id_curso')
        gestion_id = request.session.get('malla_gestion_id')
        
        if not curso_id or not gestion_id:
            return JsonResponse({'materias': []})

        # 1. Obtener materias registradas en curso_materia para este curso
        materias_en_malla = CursoMateria.objects.filter(id_curso_id=curso_id).values_list('id_materia_id', flat=True)
        
        # 2. Obtener materias que ya tienen docente asignado en este curso y gestión
        materias_ya_asignadas = AsignacionDocente.objects.filter(
            id_curso_id=curso_id, id_gestion_id=gestion_id
        ).values_list('id_materia_id', flat=True)

        # 3. Filtrar las materias que están en la malla pero que NO han sido asignadas aún
        materias_disponibles = Materia.objects.filter(
            id_materia__in=materias_en_malla
        ).exclude(
            id_materia__in=materias_ya_asignadas
        ).order_by('nombre_materia')

        data = [{'id_materia': m.id_materia, 'nombre_materia': m.nombre_materia} for m in materias_disponibles]
        return JsonResponse({'materias': data})


# --- CORRECCIÓN DE EXPORTACIÓN GENERAL Y POR CURSO EN PDF ---

def exportar_malla_general_pdf(request, id_gestion):
    gestion = get_object_or_404(Gestion, id_gestion=id_gestion)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Malla_General_{gestion.anio}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('T1', parent=styles['Heading1'], fontSize=18, leading=22, textColor=colors.HexColor("#1e3a8a"), alignment=1)
    sub_style = ParagraphStyle('S1', parent=styles['Normal'], fontSize=11, leading=14, alignment=1, textColor=colors.HexColor("#475569"))
    curso_header = ParagraphStyle('CH', parent=styles['Heading2'], fontSize=12, leading=16, textColor=colors.HexColor("#0f172a"), spaceBefore=12, spaceAfter=6)
    header_style = ParagraphStyle('HS', parent=styles['Normal'], fontSize=10, leading=12, textColor=colors.white, fontName="Helvetica-Bold")
    cell_style = ParagraphStyle('CS', parent=styles['Normal'], fontSize=9, leading=12)

    story.append(Paragraph("Consolidado de Plan de Estudios Institucional", title_style))
    story.append(Paragraph(f"Reporte General de Asignaciones Docentes - Gestión: {gestion.anio}", sub_style))
    story.append(Spacer(1, 15))

    cursos = Curso.objects.all().order_by('nombre', 'paralelo')
    for c in list(cursos):
        story.append(Paragraph(f"Curso: {c.nombre} \"{c.paralelo}\" — {c.nivel}", curso_header))
        # CORRECCIÓN AQUÍ: Se añadió select_related para evitar fallos de renderizado del objeto Persona
        elementos = AsignacionDocente.objects.filter(id_curso=c, id_gestion=gestion).select_related('id_materia', 'id_maestro__id_persona')
        
        if elementos.exists():
            data = [[Paragraph("Asignatura", header_style), Paragraph("Docente Asignado", header_style)]]
            for el in elementos:
                nom_doc = f"{el.id_maestro.id_persona.nombres} {el.id_maestro.id_persona.apellidos}"
                data.append([Paragraph(el.id_materia.nombre_materia, cell_style), Paragraph(nom_doc, cell_style)])
            
            tabla = Table(data, colWidths=[220, 300])
            tabla.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            story.append(tabla)
        else:
            story.append(Paragraph("<i>Sin asignaturas con docentes planificados.</i>", cell_style))
        story.append(Spacer(1, 10))

    doc.build(story)
    return response


def exportar_malla_curso_pdf(request, id_curso, id_gestion):
    curso = get_object_or_404(Curso, id_curso=id_curso)
    gestion = get_object_or_404(Gestion, id_gestion=id_gestion)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Plan_{curso.nombre}_{curso.paralelo}_{gestion.anio}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('T2', parent=styles['Heading1'], fontSize=20, leading=24, textColor=colors.HexColor("#0f172a"))
    meta_style = ParagraphStyle('M2', parent=styles['Normal'], fontSize=11, leading=15, textColor=colors.HexColor("#334155"))
    header_style = ParagraphStyle('H2', parent=styles['Normal'], fontSize=11, leading=13, textColor=colors.white, fontName="Helvetica-Bold")
    cell_style = ParagraphStyle('C2', parent=styles['Normal'], fontSize=10, leading=14)

    story.append(Paragraph(f"Plan de Asignaturas y Personal Docente", title_style))
    story.append(Spacer(1, 8))
    story.append(Paragraph(f"<b>Curso:</b> {curso.nombre} \"{curso.paralelo}\"<br/><b>Nivel:</b> {curso.nivel}<br/><b>Gestión Académica:</b> {gestion.anio}", meta_style))
    story.append(Spacer(1, 20))

    elementos = AsignacionDocente.objects.filter(id_curso=curso, id_gestion=gestion).select_related('id_materia', 'id_maestro__id_persona')
    
    if elementos.exists():
        data = [[Paragraph("Código Asignatura", header_style), Paragraph("Descripción Asignatura", header_style), Paragraph("Docente Responsable", header_style)]]
        for el in elementos:
            nom_doc = f"{el.id_maestro.id_persona.nombres} {el.id_maestro.id_persona.apellidos}"
            data.append([
                Paragraph(f"MAT-{el.id_materia.id_materia}", cell_style),
                Paragraph(el.id_materia.nombre_materia, cell_style),
                Paragraph(nom_doc, cell_style)
            ])
        
        tabla = Table(data, colWidths=[120, 200, 210])
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(tabla)
    else:
        story.append(Paragraph("No se encontraron registros de asignación para este curso en la gestión seleccionada.", cell_style))

    doc.build(story)
    return response