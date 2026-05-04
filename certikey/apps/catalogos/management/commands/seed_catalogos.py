from django.core.management.base import BaseCommand
from apps.catalogos.infrastructure.models import (
    Rol, EstadoVerificacion, EstadoPrograma,
    TipoPrograma, Modalidad, NivelAcademico, Moneda, Categoria,
)


class Command(BaseCommand):
    """
    Comando para poblar los catálogos iniciales necesarios para el funcionamiento del sistema.
    Se puede ejecutar con: python manage.py seed_catalogos
    """
    help = 'Pobla los catálogos iniciales necesarios para el funcionamiento del sistema.'

    def handle(self, *args, **options):
        self._seed_roles()
        self._seed_estados_verificacion()
        self._seed_estados_programa()
        self._seed_tipos_programa()
        self._seed_modalidades()
        self._seed_niveles()
        self._seed_monedas()
        self._seed_categorias()
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

    def _seed_categorias(self):
        from django.utils.text import slugify
        datos = [
            {'nombre': 'Tecnología y Software',     'slug': 'tecnologia-y-software',     'icono': 'pi pi-desktop',       'descripcion': 'Programación, desarrollo de software y herramientas tecnológicas'},
            {'nombre': 'Ingeniería',                 'slug': 'ingenieria',                'icono': 'pi pi-cog',           'descripcion': 'Disciplinas de ingeniería civil, mecánica, eléctrica y afines'},
            {'nombre': 'Ciberseguridad',             'slug': 'ciberseguridad',            'icono': 'pi pi-shield',        'descripcion': 'Seguridad informática, hacking ético y protección de datos'},
            {'nombre': 'Diseño y Multimedia',        'slug': 'diseno-y-multimedia',       'icono': 'pi pi-palette',       'descripcion': 'Diseño gráfico, UX/UI, fotografía y producción audiovisual'},
            {'nombre': 'Administración y Negocios',  'slug': 'administracion-y-negocios', 'icono': 'pi pi-briefcase',     'descripcion': 'Gestión empresarial, finanzas, marketing y emprendimiento'},
            {'nombre': 'Educación y Docencia',       'slug': 'educacion-y-docencia',      'icono': 'pi pi-book',          'descripcion': 'Pedagogía, formación docente y metodologías de enseñanza'},
            {'nombre': 'Salud y Medicina',           'slug': 'salud-y-medicina',          'icono': 'pi pi-heart',         'descripcion': 'Ciencias de la salud, enfermería, nutrición y medicina'},
            {'nombre': 'Gastronomía',                'slug': 'gastronomia',               'icono': 'pi pi-star',          'descripcion': 'Cocina, pastelería, barismo y artes culinarias'},
            {'nombre': 'Derecho y Legal',            'slug': 'derecho-y-legal',           'icono': 'pi pi-verified',      'descripcion': 'Ciencias jurídicas, derecho corporativo y legislación'},
            {'nombre': 'Idiomas',                    'slug': 'idiomas',                   'icono': 'pi pi-globe',         'descripcion': 'Aprendizaje y certificación en lenguas extranjeras'},
            {'nombre': 'Ciencias Exactas',           'slug': 'ciencias-exactas',          'icono': 'pi pi-calculator',    'descripcion': 'Matemáticas, física, química y estadística'},
            {'nombre': 'Arte y Humanidades',         'slug': 'arte-y-humanidades',        'icono': 'pi pi-image',         'descripcion': 'Bellas artes, literatura, filosofía y ciencias sociales'},
        ]
        for d in datos:
            Categoria.objects.get_or_create(slug=d['slug'], defaults={**d, 'activa': True})
        self.stdout.write('  ✓ Categorías')
