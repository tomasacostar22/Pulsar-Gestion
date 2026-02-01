from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout


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
