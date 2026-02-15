from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from .models import Mensaje
from tareas.models import Anuncio

Usuario = get_user_model()


@login_required
def bandeja(request):
    vista = request.GET.get("vista", "recibidos")

    if vista == "enviados":
        mensajes = Mensaje.objects.filter(remitente=request.user).select_related("destinatario")
    else:
        mensajes = Mensaje.objects.filter(destinatario=request.user).select_related("remitente")

    anuncios = Anuncio.objects.select_related("autor").all()[:20]
    context = {"mensajes": mensajes, "vista": vista, "seccion_activa": "mensajes", "anuncios": anuncios}

    if request.headers.get("HX-Request"):
        return render(request, "mensajes/parciales/lista_mensajes.html", context)

    return render(request, "mensajes/bandeja.html", context)


@login_required
def enviar_mensaje(request):
    usuarios = Usuario.objects.exclude(id=request.user.id)
    error = None

    if request.method == "POST":
        destinatario_id = request.POST.get("destinatario", "")
        titulo = request.POST.get("titulo", "").strip()
        contenido = request.POST.get("contenido", "").strip()

        if not destinatario_id or not titulo or not contenido:
            error = "Todos los campos son obligatorios."
        else:
            Mensaje.objects.create(
                remitente=request.user,
                destinatario_id=destinatario_id,
                titulo=titulo,
                contenido=contenido,
            )
            return redirect("mensajes:bandeja")

    return render(request, "mensajes/enviar.html", {
        "usuarios": usuarios,
        "error": error,
    })
