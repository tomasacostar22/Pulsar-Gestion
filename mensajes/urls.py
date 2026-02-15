from django.urls import path
from . import views

app_name = "mensajes"

urlpatterns = [
    path("", views.bandeja, name="bandeja"),
    path("enviar/", views.enviar_mensaje, name="enviar_mensaje"),
]
