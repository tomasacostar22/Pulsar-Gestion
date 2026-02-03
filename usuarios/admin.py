
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    # Campos que se muestran en la lista de usuarios
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    
    # Campos editables directamente desde la lista (opcional)
    list_editable = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    
    # Filtros en la barra lateral
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    
    # Barra de búsqueda
    search_fields = ('username', 'first_name', 'last_name', 'email')
    
    # Organización de campos en el formulario de edición
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información personal', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Fechas importantes', {'fields': ('last_login', 'date_joined')}),
    )
    
    # Campos para cuando creas un nuevo usuario
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )