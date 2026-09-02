from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.db.models import Q
from web.models import PersonalAdministrativo, Persona, Usuario


class GestionPersonalView(View):

    template_name = 'director/gestion_personal.html'

    def get_context(self, search_query=None):

        personal = PersonalAdministrativo.objects.select_related(
            'id_persona'
        ).all()

        if search_query:
            personal = personal.filter(
                Q(id_persona__nombres__icontains=search_query) |
                Q(id_persona__apellidos__icontains=search_query) |
                Q(id_persona__dni_cedula__icontains=search_query) |
                Q(cargo__icontains=search_query)
            )

        total = PersonalAdministrativo.objects.count()

        con_usuario = Usuario.objects.filter(
            id_persona__in=
            PersonalAdministrativo.objects.values_list(
                'id_persona_id',
                flat=True
            )
        ).count()

        cargos = PersonalAdministrativo.objects.exclude(
            cargo__isnull=True
        ).exclude(
            cargo=''
        ).values(
            'cargo'
        ).distinct().count()

        return {
            'personal': personal,
            'search_query': search_query or '',
            'referencias': {
                'total': total,
                'cargos': cargos,
                'con_usuario': con_usuario,
                'sin_usuario': total - con_usuario
            }
        }

    def get(self, request):

        if 'id_usuario' not in request.session:
            return redirect('/login/')

        if request.session.get('nombre_rol') != 'Director':
            return redirect('/login/')

        context = self.get_context(
            request.GET.get('search')
        )

        return render(
            request,
            self.template_name,
            context
        )

    def post(self, request):

        action = request.POST.get('action')

        if action == 'create':

            persona = Persona.objects.create(
                dni_cedula=request.POST.get('dni_cedula'),
                nombres=request.POST.get('nombres'),
                apellidos=request.POST.get('apellidos'),
                genero=request.POST.get('genero'),
                fecha_nacimiento=request.POST.get('fecha_nacimiento'),
                telefono=request.POST.get('telefono')
            )

            PersonalAdministrativo.objects.create(
                id_persona=persona,
                cargo=request.POST.get('cargo')
            )

            messages.success(
                request,
                'Personal administrativo registrado correctamente.'
            )

        elif action == 'update':

            admin = get_object_or_404(
                PersonalAdministrativo,
                id_admin=request.POST.get('id_admin')
            )

            persona = admin.id_persona

            persona.dni_cedula = request.POST.get('dni_cedula')
            persona.nombres = request.POST.get('nombres')
            persona.apellidos = request.POST.get('apellidos')
            persona.genero = request.POST.get('genero')
            persona.fecha_nacimiento = request.POST.get(
                'fecha_nacimiento'
            )
            persona.telefono = request.POST.get('telefono')

            persona.save()

            admin.cargo = request.POST.get('cargo')
            admin.save()

            messages.success(
                request,
                'Datos actualizados correctamente.'
            )

        elif action == 'delete':

            admin = get_object_or_404(
                PersonalAdministrativo,
                id_admin=request.POST.get('id_admin')
            )

            persona = admin.id_persona

            admin.delete()

            try:
                persona.delete()
            except:
                pass

            messages.success(
                request,
                'Registro eliminado correctamente.'
            )

        return redirect('gestion_personal')