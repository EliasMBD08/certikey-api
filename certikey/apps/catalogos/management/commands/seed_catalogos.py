from django.core.management.base import BaseCommand
from apps.catalogos.infrastructure.models import (
    Rol, EstadoVerificacion, EstadoPrograma,
    TipoPrograma, Modalidad, NivelAcademico, Moneda,
)


class Command(BaseCommand):
    help = 'Pobla los catálogos iniciales necesarios para el funcionamiento del sistema.'

    def handle(self, *args, **options):
        self._seed_roles()
        self._seed_estados_verificacion()
        self._seed_estados_programa()
        self._seed_tipos_programa()
        self._seed_modalidades()
        self._seed_niveles()
        self._seed_monedas()
        self.stdout.write(self.style.SUCCESS('Catálogos iniciales cargados correctamente.'))

    def _seed_roles(self):
        datos = [
            {'nombre': 'Admin', 'slug': 'admin', 'es_publico': False, 'descripcion': 'Administrador del sistema'},
            {'nombre': 'Certificadora', 'slug': 'certificadora', 'es_publico': True, 'descripcion': 'Institución educativa'},
            {'nombre': 'Estudiante', 'slug': 'estudiante', 'es_publico': True, 'descripcion': 'Estudiante de la plataforma'},
        ]
        for d in datos:
            Rol.objects.get_or_create(slug=d['slug'], defaults=d)
        self.stdout.write('  ✓ Roles')

    def _seed_estados_verificacion(self):
        datos = [
            {'nombre': 'Pendiente', 'slug': 'pendiente', 'permite_publicar': False},
            {'nombre': 'Verificada', 'slug': 'verificada', 'permite_publicar': True},
            {'nombre': 'Suspendida', 'slug': 'suspendida', 'permite_publicar': False},
        ]
        for d in datos:
            EstadoVerificacion.objects.get_or_create(slug=d['slug'], defaults=d)
        self.stdout.write('  ✓ Estados de verificación')

    def _seed_estados_programa(self):
        datos = [
            {'nombre': 'Borrador', 'slug': 'borrador', 'es_visible_publico': False},
            {'nombre': 'Publicado', 'slug': 'publicado', 'es_visible_publico': True},
            {'nombre': 'Pausado', 'slug': 'pausado', 'es_visible_publico': False},
            {'nombre': 'Archivado', 'slug': 'archivado', 'es_visible_publico': False},
        ]
        for d in datos:
            EstadoPrograma.objects.get_or_create(slug=d['slug'], defaults=d)
        self.stdout.write('  ✓ Estados de programa')

    def _seed_tipos_programa(self):
        nombres = ['Curso', 'Diplomado', 'Carrera Técnica', 'Carrera Universitaria', 'Bootcamp', 'Certificación']
        from django.utils.text import slugify
        for nombre in nombres:
            TipoPrograma.objects.get_or_create(slug=slugify(nombre), defaults={'nombre': nombre, 'activo': True})
        self.stdout.write('  ✓ Tipos de programa')

    def _seed_modalidades(self):
        datos = [
            {'nombre': 'Presencial', 'slug': 'presencial'},
            {'nombre': 'Virtual', 'slug': 'virtual'},
            {'nombre': 'Híbrido', 'slug': 'hibrido'},
        ]
        for d in datos:
            Modalidad.objects.get_or_create(slug=d['slug'], defaults=d)
        self.stdout.write('  ✓ Modalidades')

    def _seed_niveles(self):
        datos = [
            {'nombre': 'Sin requisitos', 'slug': 'sin-requisitos', 'orden': 0},
            {'nombre': 'Básico', 'slug': 'basico', 'orden': 1},
            {'nombre': 'Intermedio', 'slug': 'intermedio', 'orden': 2},
            {'nombre': 'Avanzado', 'slug': 'avanzado', 'orden': 3},
        ]
        for d in datos:
            NivelAcademico.objects.get_or_create(slug=d['slug'], defaults=d)
        self.stdout.write('  ✓ Niveles académicos')

    def _seed_monedas(self):
        datos = [
            {'nombre': 'Sol Peruano', 'codigo_iso': 'PEN', 'simbolo': 'S/'},
            {'nombre': 'Dólar Americano', 'codigo_iso': 'USD', 'simbolo': '$'},
            {'nombre': 'Euro', 'codigo_iso': 'EUR', 'simbolo': '€'},
        ]
        for d in datos:
            Moneda.objects.get_or_create(codigo_iso=d['codigo_iso'], defaults=d)
        self.stdout.write('  ✓ Monedas')
