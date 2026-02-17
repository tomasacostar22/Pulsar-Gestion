from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden

from .models import Tarea, Anuncio

Usuario = get_user_model()


@login_required
def principal(request):
    vista = request.GET.get("vista", "propias")
    estado = request.GET.get("estado", "PENDIENTE")

    if vista == "supervisar":
        tareas = Tarea.objects.filter(supervisor=request.user).exclude(responsable=request.user)
    elif vista == "asignadas":
        tareas = Tarea.objects.filter(responsable=request.user).exclude(supervisor=request.user)
    else:
        # propias: autoasignadas (soy responsable Y supervisor)
        tareas = Tarea.objects.filter(responsable=request.user, supervisor=request.user)

    tareas = tareas.filter(estado=estado).order_by("-fecha_creacion")

    anuncios = Anuncio.objects.select_related("autor").all()[:20]

    context = {"tareas": tareas, "vista": vista, "estado": estado, "anuncios": anuncios, "seccion_activa": "tareas"}

    if request.headers.get("HX-Request"):
        return render(request, "tareas/parciales/lista_tareas.html", context)

    return render(request, "tareas/principal.html", context)


@login_required
def crear_anuncio(request):
    if request.method == "POST":
        titulo = request.POST.get("titulo", "").strip()
        contenido = request.POST.get("contenido", "").strip()
        if titulo and contenido:
            Anuncio.objects.create(autor=request.user, titulo=titulo, contenido=contenido)

    anuncios = Anuncio.objects.select_related("autor").all()[:20]

    if request.headers.get("HX-Request"):
        return render(request, "tareas/parciales/lista_anuncios.html", {"anuncios": anuncios, "user": request.user})

    vista = request.POST.get("vista", "realizar")
    return redirect(f"/tareas/?vista={vista}")


@login_required
def eliminar_anuncio(request, anuncio_id):
    if request.method == "POST":
        try:
            anuncio = Anuncio.objects.get(id=anuncio_id, autor=request.user)
            anuncio.delete()
        except Anuncio.DoesNotExist:
            pass

    anuncios = Anuncio.objects.select_related("autor").all()[:20]

    if request.headers.get("HX-Request"):
        return render(request, "tareas/parciales/lista_anuncios.html", {"anuncios": anuncios, "user": request.user})

    return redirect("/tareas/")


@login_required
def crear_tarea(request):
    modo = request.GET.get("modo", request.POST.get("modo", ""))
    es_propia = modo == "propia"
    usuarios = Usuario.objects.exclude(id=request.user.id) if not es_propia else None
    error = None

    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        descripcion = request.POST.get("descripcion", "").strip()
        fecha_limite = request.POST.get("fecha_limite", "")
        prioridad = request.POST.get("prioridad", "MEDIA")

        if es_propia:
            responsable_id = request.user.id
        else:
            responsable_id = request.POST.get("responsable", "")

        if not nombre or not fecha_limite or (not es_propia and not responsable_id):
            error = "Todos los campos obligatorios deben completarse."
        else:
            Tarea.objects.create(
                nombre=nombre,
                descripcion=descripcion,
                fecha_limite=fecha_limite,
                prioridad=prioridad,
                responsable_id=responsable_id,
                supervisor=request.user,
            )
            if es_propia:
                return redirect("/tareas/?vista=propias")
            return redirect("/tareas/?vista=supervisar")

    return render(request, "tareas/crear.html", {
        "usuarios": usuarios,
        "prioridades": Tarea.Prioridad.choices,
        "error": error,
        "es_propia": es_propia,
    })


@login_required
def finalizar_tarea(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id)

    if request.user != tarea.responsable:
        return HttpResponseForbidden("No tenes permiso para finalizar esta tarea.")

    if request.method == "POST":
        tarea.estado = Tarea.Estado.FINALIZADA
        tarea.save()

    vista = request.GET.get("vista", "propias")
    estado = request.GET.get("estado", "PENDIENTE")

    if vista == "propias":
        tareas = Tarea.objects.filter(responsable=request.user, supervisor=request.user)
    else:
        tareas = Tarea.objects.filter(responsable=request.user).exclude(supervisor=request.user)

    tareas = tareas.filter(estado=estado).order_by("-fecha_creacion")
    context = {"tareas": tareas, "vista": vista, "estado": estado}

    if request.headers.get("HX-Request"):
        return render(request, "tareas/parciales/lista_tareas.html", context)

    return redirect(f"/tareas/?vista={vista}&estado={estado}")


@login_required
def cancelar_tarea(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id)

    if request.user != tarea.supervisor:
        return HttpResponseForbidden("No tenes permiso para cancelar esta tarea.")

    if request.method == "POST" and tarea.estado == Tarea.Estado.PENDIENTE:
        tarea.estado = Tarea.Estado.CANCELADA
        tarea.save()

    vista = request.GET.get("vista", "supervisar")
    estado = request.GET.get("estado", "PENDIENTE")

    tareas = Tarea.objects.filter(supervisor=request.user).exclude(responsable=request.user).filter(estado=estado).order_by("-fecha_creacion")
    context = {"tareas": tareas, "vista": vista, "estado": estado}

    if request.headers.get("HX-Request"):
        return render(request, "tareas/parciales/lista_tareas.html", context)

    return redirect(f"/tareas/?vista={vista}&estado={estado}")
