from django.urls import path
from . import views

urlpatterns = [
    path("", views.principal, name="principal"),
    path("crear/", views.crear_tarea, name="crear_tarea"),
    path("anuncio/", views.crear_anuncio, name="crear_anuncio"),
]