from django.views.generic import TemplateView

class IndexDashboardView(TemplateView):
    template_name = 'web/index.html'