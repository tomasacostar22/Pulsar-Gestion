from django.urls import path
from . import views

urlpatterns = [
    path("", views.principal, name="principal"),
    path("crear/", views.crear_tarea, name="crear_tarea"),
    path("anuncio/", views.crear_anuncio, name="crear_anuncio"),
    path("anuncio/<int:anuncio_id>/eliminar/", views.eliminar_anuncio, name="eliminar_anuncio"),
    path("<int:tarea_id>/finalizar/", views.finalizar_tarea, name="finalizar_tarea"),
    path("<int:tarea_id>/cancelar/", views.cancelar_tarea, name="cancelar_tarea"),
]