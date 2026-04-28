from django.contrib import admin

from apps.resenas.infrastructure.models import ResenaPrograma, ResenaCertificadora


@admin.register(ResenaPrograma)
class ResenaProgramaAdmin(admin.ModelAdmin):
    list_display = ('id', 'estudiante', 'programa', 'calificacion', 'fecha_creacion', 'activo')
    list_filter = ('calificacion', 'activo')
    search_fields = ('comentario',)
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')


@admin.register(ResenaCertificadora)
class ResenaCertificadoraAdmin(admin.ModelAdmin):
    list_display = ('id', 'estudiante', 'certificadora', 'calificacion', 'fecha_creacion', 'activo')
    list_filter = ('calificacion', 'activo')
    search_fields = ('comentario',)
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
