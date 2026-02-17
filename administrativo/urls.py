from django.urls import path
from . import views

app_name = "administrativo"

urlpatterns = [
    path("horarios/", views.horarios, name="horarios"),
]
