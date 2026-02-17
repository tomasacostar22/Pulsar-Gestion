from django.urls import path
from . import views

app_name = "administrativo"

urlpatterns = [
    path("horarios/", views.horarios, name="horarios"),
    path("tareas/", views.supervisar_tareas, name="supervisar_tareas"),
]
