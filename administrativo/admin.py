from django.contrib import admin
from .models import HorarioLaboral


@admin.register(HorarioLaboral)
class HorarioLaboralAdmin(admin.ModelAdmin):
    list_display = ("empleado",)
