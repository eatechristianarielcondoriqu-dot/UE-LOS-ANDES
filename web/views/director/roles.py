from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from web.models import Rol

class GestionRolesView(View):
    template_name = 'director/roles.html'

    def get_context(self, request):
        # Obtener todos los roles registrados en la base de datos
        roles = Rol.objects.all().order_by('id_rol')
        
        # Métrica de referencia rápida para las tarjetas de información
        total_roles = roles.count()

        return {
            'nombres': request.session.get('nombres', 'Administrador'),
            'nombre_rol': request.session.get('nombre_rol', 'Administrativo'),
            'roles': roles,
            'total_roles': total_roles
        }

    def get(self, request):
        if 'id_usuario' not in request.session:
            return redirect('/login/')
        return render(request, self.template_name, self.get_context(request))

    def post(self, request):
        if 'id_usuario' not in request.session:
            return redirect('/login/')

        action = request.POST.get('action')

        # --- ACCIÓN 1: CREAR ROL ---
        if action == 'crear_rol':
            nombre = request.POST.get('nombre_rol', '').strip()
            if not nombre:
                messages.error(request, "El nombre del rol no puede estar vacío.")
                return redirect('gestion_roles')

            # Validación de duplicados
            if Rol.objects.filter(nombre_rol__iexact=nombre).exists():
                messages.error(request, f"El rol '{nombre}' ya se encuentra registrado.")
                return redirect('gestion_roles')

            Rol.objects.create(nombre_rol=nombre)
            messages.success(request, f"Rol '{nombre}' registrado exitosamente.")
            return redirect('gestion_roles')

        # --- ACCIÓN 2: EDITAR ROL ---
        elif action == 'editar_rol':
            id_rol_raw = request.POST.get('id_rol', '').strip()
            nombre = request.POST.get('nombre_rol', '').strip()
            
            # Control de seguridad contra IDs vacíos
            if not id_rol_raw:
                messages.error(request, "Error de transferencia: No se recibió un ID de rol válido.")
                return redirect('gestion_roles')
            
            try:
                # Conversión segura a entero para evitar fallos de sintaxis en BD
                id_rol = int(id_rol_raw)
                rol = get_object_or_404(Rol, id_rol=id_rol)
                
                if not nombre:
                    messages.error(request, "El nombre del rol modificado no puede estar vacío.")
                    return redirect('gestion_roles')

                # Verificar que no colisione con otro rol existente
                if Rol.objects.filter(nombre_rol__iexact=nombre).exclude(id_rol=id_rol).exists():
                    messages.error(request, f"Ya existe otro rol con el nombre '{nombre}'.")
                    return redirect('gestion_roles')

                rol.nombre_rol = nombre
                rol.save()
                messages.success(request, "Rol actualizado correctamente.")
                
            except ValueError:
                messages.error(request, "El identificador del rol debe ser un valor numérico válido.")
            
            return redirect('gestion_roles')

        # --- ACCIÓN 3: ELIMINAR ROL ---
        elif action == 'eliminar_rol':
            id_rol_raw = request.POST.get('id_rol', '').strip()
            
            if not id_rol_raw:
                messages.error(request, "Error de transferencia: No se especificó el ID a eliminar.")
                return redirect('gestion_roles')
                
            try:
                id_rol = int(id_rol_raw)
                rol = get_object_or_404(Rol, id_rol=id_rol)
                
                nombre_eliminado = rol.nombre_rol
                rol.delete()
                messages.success(request, f"El rol '{nombre_eliminado}' ha sido eliminado del sistema.")
                
            except ValueError:
                messages.error(request, "El identificador del rol a eliminar no es válido.")
                
            return redirect('gestion_roles')

        return redirect('gestion_roles')