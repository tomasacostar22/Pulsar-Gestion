def permisos_administrativo(request):
    if request.user.is_authenticated:
        es_gerencia = request.user.groups.filter(name="Gerencia").exists()
    else:
        es_gerencia = False
    return {"es_gerencia": es_gerencia}
