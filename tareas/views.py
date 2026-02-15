from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from .models import Tarea, Anuncio

Usuario = get_user_model()


@login_required
def principal(request):
    vista = request.GET.get("vista", "realizar")
    if vista == "supervisar":
        tareas = Tarea.objects.filter(supervisor=request.user).order_by("-fecha_creacion")
    else:
        tareas = Tarea.objects.filter(responsable=request.user).order_by("-fecha_creacion")

    anuncios = Anuncio.objects.select_related("autor").all()[:20]

    context = {"tareas": tareas, "vista": vista, "anuncios": anuncios}

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
    usuarios = Usuario.objects.all()
    error = None

    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        descripcion = request.POST.get("descripcion", "").strip()
        fecha_limite = request.POST.get("fecha_limite", "")
        prioridad = request.POST.get("prioridad", "MEDIA")
        responsable_id = request.POST.get("responsable", "")

        if not nombre or not fecha_limite or not responsable_id:
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
            return redirect("/tareas/?vista=supervisar")

    return render(request, "tareas/crear.html", {
        "usuarios": usuarios,
        "prioridades": Tarea.Prioridad.choices,
        "error": error,
    })
