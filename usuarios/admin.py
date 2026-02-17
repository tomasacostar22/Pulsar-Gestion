
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    # Campos que se muestran en la lista de usuarios
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    
    list_display_links = ('username', 'email', 'first_name', 'last_name')
    
    # Filtros en la barra lateral
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    
    # Barra de búsqueda
    search_fields = ('username', 'first_name', 'last_name', 'email')

    # Widget de selección doble para grupos y permisos
    filter_horizontal = ('groups', 'user_permissions')
    
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
