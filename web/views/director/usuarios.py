from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.db.models import Q, Count
from web.models import Usuario, Persona, Rol, Maestro, Estudiante, PersonalAdministrativo, PadreFamilia

class GestionUsuariosView(View):
    template_name = 'director/gestion_usuarios.html'

    def get_context(self, request, search_query=None):
        """Carga datos primarios, lógica de búsqueda, filtrado riguroso de sub-roles y métricas"""
        usuarios_queryset = Usuario.objects.select_related('id_persona', 'id_role').all()

        # OPERACIÓN: BUSCAR USUARIO
        if search_query:
            usuarios_queryset = usuarios_queryset.filter(
                Q(username__icontains=search_query) |
                Q(id_persona__nombres__icontains=search_query) |
                Q(id_persona__apellidos__icontains=search_query) |
                Q(id_persona__dni_cedula__icontains=search_query)
            )

        # CONSULTAS DE REFERENCIA (Estadísticas para el panel superior)
        total_usuarios = Usuario.objects.count()
        usuarios_activos = Usuario.objects.filter(activo=True).count()
        usuarios_inactivos = total_usuarios - usuarios_activos
        
        roles_count = Usuario.objects.values('id_role__nombre_rol').annotate(total=Count('id_usuario'))
        distribucion_roles = {item['id_role__nombre_rol'].lower(): item['total'] for item in roles_count}

        # --- LÓGICA DE CONTROL: SWITCH PARA VER/OCULTAR ESTUDIANTES ---
        if request.GET.get('toggle_estudiantes') == '1':
            # Invierte el estado guardado en la sesión (por defecto False)
            request.session['ver_estudiantes_en_select'] = not request.session.get('ver_estudiantes_en_select', False)
            
        ver_estudiantes = request.session.get('ver_estudiantes_en_select', False)

        # --- FILTRADO AVANZADO DE PERSONAS DISPONIBLES (PARA CREAR USUARIOS) ---
        # 1. Obtener IDs de personas que ya tienen una cuenta creada para excluirlas
        personas_con_cuenta = Usuario.objects.values_list('id_persona_id', flat=True)

        # 2. Traer todas las personas que NO tienen usuario asignado
        personas_disponibles = Persona.objects.exclude(id_persona__in=personas_con_cuenta)
        
        # --- OBTENER LOS IDS DE MANERA ULTRA-EFICIENTE (FUERA DEL BUCLE) ---
        ids_maestros = set(Maestro.objects.values_list('id_persona_id', flat=True))
        ids_padres = set(PadreFamilia.objects.values_list('id_persona_id', flat=True))
        ids_admins = set(PersonalAdministrativo.objects.values_list('id_persona_id', flat=True))
        ids_estudiantes = set(Estudiante.objects.values_list('id_persona_id', flat=True))
        
        personas_filtradas = []
        # --- EVALUAR LAS PERSONAS DISPONIBLES ---
        for p in personas_disponibles:
            persona_id = p.pk  

            # Comprobación de existencia matemática rápida en los sets
            es_maestro = persona_id in ids_maestros
            es_padre = persona_id in ids_padres
            es_admin = persona_id in ids_admins
            es_estudiante = persona_id in ids_estudiantes

            # Validación obligatoria: Debe pertenecer al menos a un sub-rol institucional
            if not (es_maestro or es_padre or es_admin or es_estudiante):
                continue

            # Si es únicamente estudiante y el switch está apagado, se excluye
            if es_estudiante and not ver_estudiantes:
                if not (es_maestro or es_padre or es_admin):
                    continue

            # Mapeo exacto de los tags visuales basados en sus tablas relacionales
            tags = []
            if es_admin: tags.append("Personal Administrativo")
            if es_maestro: tags.append("Maestro")
            if es_padre: tags.append("Padre de Familia")
            if es_estudiante: tags.append("Estudiante")
            
            p.rol_tag = " / ".join(tags)
            personas_filtradas.append(p)

        return {
            # VARIABLES COMPATIBLES CON TU NAVBAR DINÁMICO
            'nombres': request.session.get('nombres', 'Director'),
            'nombre_rol': request.session.get('nombre_rol', 'Director'),

            'usuarios': usuarios_queryset,
            'personas': personas_filtradas, 
            'roles': Rol.objects.all(),
            'search_query': search_query or '',
            'ver_estudiantes': ver_estudiantes, 
            'referencias': {
                'total': total_usuarios,
                'activos': usuarios_activos,
                'inactivos': usuarios_inactivos,
                'maestros': distribucion_roles.get('maestro', 0),
                'padres': distribucion_roles.get('padre', 0),
                'directores': distribucion_roles.get('director', 0),
            }
        }

    def get(self, request):
        if 'id_usuario' not in request.session or request.session.get('nombre_rol') != 'Director':
            return redirect('/login/')
        
        # Si se presionó el botón del switch, redirigimos limpiando el parámetro para mantener la URL estética
        if 'toggle_estudiantes' in request.GET:
            self.get_context(request) # Ejecuta la inversión del estado en sesión
            search_param = request.GET.get('search', '')
            url = f"{request.path}?search={search_param}" if search_param else request.path
            return redirect(url)

        search_query = request.GET.get('search')
        context = self.get_context(request, search_query)
        return render(request, self.template_name, context)

    def post(self, request):
        if 'id_usuario' not in request.session or request.session.get('nombre_rol') != 'Director':
            return redirect('/login/')

        action = request.POST.get('action')

        # ---- OPERACIÓN: INSERTAR DATOS ----
        if action == 'create':
            try:
                id_persona = request.POST.get('id_persona')
                id_role = request.POST.get('id_role')
                username = request.POST.get('username')
                password_raw = request.POST.get('password')

                if Usuario.objects.filter(username=username).exists():
                    messages.error(request, f"El nombre de usuario '{username}' ya está en uso.")
                    return redirect('gestion_usuarios')

                Usuario.objects.create(
                    id_persona=Persona.objects.get(id_persona=id_persona),
                    id_role=Rol.objects.get(id_rol=id_role),
                    username=username,
                    password=make_password(password_raw),
                    activo=True
                )
                messages.success(request, "Usuario registrado exitosamente.")
            except Exception as e:
                messages.error(request, f"Error al insertar datos: {str(e)}")

        # ---- OPERACIÓN: EDITAR DATOS ----
        elif action == 'update':
            try:
                id_usuario = request.POST.get('id_usuario')
                usuario = get_object_or_404(Usuario, id_usuario=id_usuario)

                usuario.id_persona = Persona.objects.get(id_persona=request.POST.get('id_persona'))
                usuario.id_role = Rol.objects.get(id_rol=request.POST.get('id_role'))
                usuario.username = request.POST.get('username')
                
                new_password = request.POST.get('password')
                if new_password and new_password.strip() != '':
                    usuario.password = make_password(new_password)

                usuario.save()
                messages.success(request, "Datos del usuario modificados correctamente.")
            except Exception as e:
                messages.error(request, f"Error al editar datos: {str(e)}")

        # ---- OPERACIÓN: CONTROL DE ESTADOS (ACTIVAR / DESACTIVAR) ----
        elif action == 'toggle_status':
            try:
                id_usuario = request.POST.get('id_usuario')
                usuario = get_object_or_404(Usuario, id_usuario=id_usuario)
                usuario.activo = not usuario.activo
                usuario.save()
                
                estado_str = "ACTIVADO" if usuario.activo else "DESACTIVADO (Acceso denegado al sistema)"
                messages.info(request, f"El usuario @{usuario.username} ha sido {estado_str}.")
            except Exception as e:
                messages.error(request, f"Error al cambiar estado: {str(e)}")

        # ---- OPERACIÓN: ELIMINAR LÓGICAMENTE ----
        elif action == 'soft_delete':
            try:
                id_usuario = request.POST.get('id_usuario')
                usuario = get_object_or_404(Usuario, id_usuario=id_usuario)
                usuario.activo = False
                usuario.save()
                messages.warning(request, f"Usuario @{usuario.username} deshabilitado mediante eliminación lógica.")
            except Exception as e:
                messages.error(request, f"Error en desactivación lógica: {str(e)}")

        # ---- OPERACIÓN: ELIMINAR DEFINITIVAMENTE ----
        elif action == 'hard_delete':
            try:
                id_usuario = request.POST.get('id_usuario')
                usuario = get_object_or_404(Usuario, id_usuario=id_usuario)
                username_eliminado = usuario.username
                usuario.delete()
                messages.success(request, f"El usuario @{username_eliminado} fue eliminado físicamente de la base de datos.")
            except Exception as e:
                messages.error(request, f"No se pudo eliminar de raíz (Verifique restricciones de clave foránea): {str(e)}")

        return redirect('gestion_usuarios')