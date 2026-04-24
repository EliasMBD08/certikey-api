from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from apps.usuarios.infrastructure.models import Usuario, PerfilEstudiante, PerfilCertificadora


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Datos adicionales', {'fields': ('rol', 'telefono', 'foto_perfil')}),
    )
    list_display = ['username', 'email', 'first_name', 'last_name', 'rol', 'is_active']
    list_filter = ['rol', 'is_active', 'is_staff']


@admin.register(PerfilEstudiante)
class PerfilEstudianteAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'pais', 'ciudad', 'fecha_creacion']
    raw_id_fields = ['usuario']


@admin.register(PerfilCertificadora)
class PerfilCertificadoraAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'nombre_institucion', 'ruc', 'estado_verificacion', 'fecha_creacion']
    list_filter = ['estado_verificacion']
    raw_id_fields = ['usuario']
