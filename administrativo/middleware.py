from django.http import HttpResponseForbidden


class GerenciaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/administrativo/"):
            if not request.user.is_authenticated:
                from django.shortcuts import redirect
                from django.conf import settings
                return redirect(settings.LOGIN_URL)

            if not request.user.groups.filter(name="Gerencia").exists():
                return HttpResponseForbidden(
                    "<h1>Acceso denegado</h1>"
                    "<p>No tienes permiso para acceder a esta seccion.</p>"
                )

        return self.get_response(request)
