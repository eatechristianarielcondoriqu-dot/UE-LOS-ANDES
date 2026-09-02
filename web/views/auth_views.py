import requests
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.hashers import check_password
from web.models import Usuario 

class LoginView(View):
    template_name = 'web/login.html'
    recaptcha_secret = '6LfQoeUsAAAAAFA3roP6KRiOABnHcpFPxvrxc42p'

    def get(self, request):
        if 'id_usuario' in request.session:
            return redirect('/dashboard/')
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        recaptcha_response = request.POST.get('g-recaptcha-response', '')

        if not username or not password:
            return render(request, self.template_name, {'error': 'Por favor completa todos los campos'})

        if not recaptcha_response:
            return render(request, self.template_name, {'error': 'Por favor, marca la casilla "No soy un robot"'})

        # Verificación de reCAPTCHA
        verify_url = 'https://www.google.com/recaptcha/api/siteverify'
        payload = {'secret': self.recaptcha_secret, 'response': recaptcha_response}
        try:
            response = requests.post(verify_url, data=payload).json()
            if not response.get('success'):
                return render(request, self.template_name, {'error': 'Verificación de seguridad fallida.'})
        except Exception:
            return render(request, self.template_name, {'error': 'Error de conexión con el servicio de verificación.'})

        # Autenticación en PostgreSQL
        try:
            user = Usuario.objects.select_related('id_persona', 'id_role').get(username=username, activo=True)
            
            # Verificación con Hash Encriptado
            if check_password(password, user.password):
                request.session['id_usuario'] = user.id_usuario
                request.session['id_persona'] = user.id_persona.id_persona
                request.session['id_rol'] = user.id_role.id_rol
                request.session['nombre_rol'] = user.id_role.nombre_rol
                request.session['nombres'] = user.id_persona.nombres
                request.session['apellidos'] = user.id_persona.apellidos
                request.session['username'] = username
                return redirect('/dashboard/')
            else:
                return render(request, self.template_name, {'error': 'Contraseña incorrecta'})
        except Usuario.DoesNotExist:
            return render(request, self.template_name, {'error': 'Usuario no encontrado'})
        
# ==========================================
#  AGREGA ESTO AL FINAL DE TU ARCHIVO:
# ==========================================
class LogoutView(View):
    def get(self, request):
        # .flush() destruye la sesión por completo en PostgreSQL y borra la cookie del navegador
        request.session.flush()
        # Redirige al login de manera limpia
        return redirect('/login/')