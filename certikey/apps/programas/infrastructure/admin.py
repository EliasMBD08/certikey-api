from django.contrib import admin
from apps.programas.infrastructure.models import Programa


@admin.register(Programa)
class ProgramaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'certificadora', 'tipo', 'modalidad', 'estado', 'es_gratuito', 'fecha_creacion']
    list_filter = ['estado', 'tipo', 'modalidad', 'es_gratuito', 'inscripciones_abiertas']
    search_fields = ['titulo', 'slug']
    prepopulated_fields = {'slug': ('titulo',)}
    raw_id_fields = ['certificadora']
