from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from .models import HorarioLaboral
from tareas.models import Tarea

Usuario = get_user_model()

DIAS = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado"]
DIAS_DISPLAY = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado"]


@login_required
def horarios(request):
    empleado_id = request.GET.get("empleado")
    empleados = Usuario.objects.all().order_by("first_name", "last_name")
    horario = None
    mensaje = None

    if empleado_id:
        try:
            empleado = Usuario.objects.get(id=empleado_id)
        except Usuario.DoesNotExist:
            empleado = None

        if empleado:
            horario, created = HorarioLaboral.objects.get_or_create(empleado=empleado)
            if created:
                horario.refresh_from_db()

            if request.method == "POST":
                for dia in DIAS:
                    entrada = request.POST.get(f"{dia}_entrada")
                    salida = request.POST.get(f"{dia}_salida")
                    if entrada:
                        setattr(horario, f"{dia}_entrada", entrada)
                    if salida:
                        setattr(horario, f"{dia}_salida", salida)
                horario.save()
                horario.refresh_from_db()
                mensaje = "Horario actualizado correctamente."

    dias_horario = None
    if horario:
        dias_horario = list(zip(DIAS, DIAS_DISPLAY, [
            (getattr(horario, f"{d}_entrada"), getattr(horario, f"{d}_salida"))
            for d in DIAS
        ]))

    context = {
        "seccion_activa": "administrativo",
        "subseccion": "horarios",
        "empleados": empleados,
        "empleado_id": int(empleado_id) if empleado_id else None,
        "horario": horario,
        "dias_horario": dias_horario,
        "mensaje": mensaje,
    }

    if request.headers.get("HX-Request") and request.method == "GET" and not request.GET.get("full"):
        return render(request, "administrativo/parciales/horario_form.html", context)

    return render(request, "administrativo/horarios.html", context)


@login_required
def supervisar_tareas(request):
    estado = request.GET.get("estado", "")
    prioridad = request.GET.get("prioridad", "")
    empleado_id = request.GET.get("empleado", "")

    tareas = Tarea.objects.select_related("responsable", "supervisor").all()

    if estado:
        tareas = tareas.filter(estado=estado)
    if prioridad:
        tareas = tareas.filter(prioridad=prioridad)
    if empleado_id:
        tareas = tareas.filter(responsable_id=empleado_id)

    tareas = tareas.order_by("-fecha_creacion")

    empleados = Usuario.objects.all().order_by("first_name", "last_name")

    context = {
        "seccion_activa": "administrativo",
        "subseccion": "supervisar_tareas",
        "tareas": tareas,
        "empleados": empleados,
        "estado_actual": estado,
        "prioridad_actual": prioridad,
        "empleado_actual": int(empleado_id) if empleado_id else None,
        "estados": Tarea.Estado.choices,
        "prioridades": Tarea.Prioridad.choices,
    }

    if request.headers.get("HX-Request"):
        return render(request, "administrativo/parciales/lista_tareas_admin.html", context)

    return render(request, "administrativo/supervisar_tareas.html", context)
