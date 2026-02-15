from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required


def login_view(request):
    if request.user.is_authenticated:
        return redirect("principal")

    error = None
    if request.method == "POST":
        email = request.POST.get("email", "")
        password = request.POST.get("password", "")
        # Buscar usuario por email para obtener el username
        from django.contrib.auth import get_user_model
        Usuario = get_user_model()
        try:
            user_obj = Usuario.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)
        except Usuario.DoesNotExist:
            user = None

        if user is not None:
            login(request, user)
            return redirect("principal")
        else:
            error = "Correo o contrasena incorrectos."

    return render(request, "usuarios/login.html", {"error": error})


def logout_view(request):
    logout(request)
    return redirect("usuarios:login")


@login_required
def cambiar_contrasena(request):
    error = None
    exito = False

    if request.method == "POST":
        actual = request.POST.get("actual", "")
        nueva = request.POST.get("nueva", "")
        confirmar = request.POST.get("confirmar", "")

        if not request.user.check_password(actual):
            error = "La contrasena actual es incorrecta."
        elif len(nueva) < 6:
            error = "La nueva contrasena debe tener al menos 6 caracteres."
        elif nueva != confirmar:
            error = "Las contrasenas no coinciden."
        else:
            request.user.set_password(nueva)
            request.user.save()
            update_session_auth_hash(request, request.user)
            exito = True

    return render(request, "usuarios/cambiar_contrasena.html", {"error": error, "exito": exito})
