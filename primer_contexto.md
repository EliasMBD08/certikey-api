Buena observación. La solución es agregar una app de catálogos que centralice toda la data de referencia como modelos, y los demás los referencian por FK. Así también puedes administrarlos desde el panel de Django sin tocar código.

---

## Nueva arquitectura

```
apps/
├── catalogos/      # Tablas de referencia: País, Ciudad, Moneda, Roles, Estados, etc.
├── usuarios/       # Custom User + perfiles
├── programas/      # Oferta académica
└── postulaciones/  # Interés / solicitudes
```

---

## `catalogos/models.py`

```python
from django.db import models


class Pais(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    codigo_iso = models.CharField(max_length=3, unique=True)  # ISO 3166-1: PE, US, CO

    class Meta:
        verbose_name = "País"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Ciudad(models.Model):
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE, related_name="ciudades")
    nombre = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Ciudad"
        unique_together = ("pais", "nombre")
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre}, {self.pais.nombre}"


class Moneda(models.Model):
    nombre = models.CharField(max_length=50)          # Sol Peruano, Dólar, etc.
    codigo_iso = models.CharField(max_length=5, unique=True)  # PEN, USD, EUR
    simbolo = models.CharField(max_length=5)          # S/, $, €

    class Meta:
        verbose_name = "Moneda"

    def __str__(self):
        return f"{self.codigo_iso} ({self.simbolo})"


class Rol(models.Model):
    """
    Roles de usuario de la plataforma.
    El campo `es_publico` controla si aparece como opción al registrarse.
    Registros iniciales: ADMIN (no público), CERTIFICADORA, ESTUDIANTE.
    """
    nombre = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    descripcion = models.CharField(max_length=255, blank=True)
    es_publico = models.BooleanField(default=True)  # False → solo asignable por Admin

    class Meta:
        verbose_name = "Rol"

    def __str__(self):
        return self.nombre


class TipoPrograma(models.Model):
    """
    Ej: Curso, Diplomado, Carrera Técnica, Carrera Universitaria, Bootcamp.
    """
    nombre = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Tipo de Programa"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Modalidad(models.Model):
    """Ej: Presencial, Virtual, Híbrido."""
    nombre = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    descripcion = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Modalidad"

    def __str__(self):
        return self.nombre


class NivelAcademico(models.Model):
    """
    Nivel requerido para acceder al programa.
    El campo `orden` permite comparar niveles entre sí.
    Ej: Sin requisitos (0), Básico (1), Intermedio (2), Avanzado (3).
    """
    nombre = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    orden = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = "Nivel Académico"
        ordering = ["orden"]

    def __str__(self):
        return self.nombre


class EstadoPrograma(models.Model):
    """
    Estado del ciclo de vida del programa.
    Ej: Borrador, Publicado, Pausado, Archivado.
    """
    nombre = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    descripcion = models.CharField(max_length=255, blank=True)
    es_visible_publico = models.BooleanField(default=False)  # Solo "Publicado" = True

    class Meta:
        verbose_name = "Estado de Programa"

    def __str__(self):
        return self.nombre


class EstadoVerificacion(models.Model):
    """
    Estado de verificación de una Certificadora por el Admin.
    Ej: Pendiente, Verificada, Suspendida.
    """
    nombre = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    permite_publicar = models.BooleanField(default=False)  # Solo "Verificada" = True

    class Meta:
        verbose_name = "Estado de Verificación"

    def __str__(self):
        return self.nombre


class EstadoPostulacion(models.Model):
    """
    Estado del interés / postulación de un estudiante.
    Ej: Guardado, Contactado, Inscrito, Cancelado.
    """
    nombre = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    descripcion = models.CharField(max_length=255, blank=True)
    es_estado_final = models.BooleanField(default=False)  # Inscrito / Cancelado = True

    class Meta:
        verbose_name = "Estado de Postulación"

    def __str__(self):
        return self.nombre


class Categoria(models.Model):
    """Área de conocimiento. Ej: Tecnología, Salud, Negocios."""
    nombre = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    icono = models.CharField(max_length=50, blank=True)
    descripcion = models.TextField(blank=True)
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Categoría"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Tag(models.Model):
    """Etiquetas para búsqueda y filtrado fino."""
    nombre = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.nombre
```

---

## `usuarios/models.py`

```python
from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """
    AUTH_USER_MODEL de la plataforma.
    El rol se asigna mediante FK a catalogos.Rol.
    Al registrarse, el serializer filtra solo roles con es_publico=True.
    """
    rol = models.ForeignKey(
        "catalogos.Rol",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="usuarios",
    )
    telefono = models.CharField(max_length=20, blank=True)
    foto_perfil = models.ImageField(upload_to="perfiles/", null=True, blank=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Usuario"

    def es_admin(self):
        return self.is_staff or (self.rol and self.rol.slug == "admin")

    def es_certificadora(self):
        return self.rol and self.rol.slug == "certificadora"

    def es_estudiante(self):
        return self.rol and self.rol.slug == "estudiante"


class PerfilEstudiante(models.Model):
    """
    Perfil extendido del estudiante.
    Se crea automáticamente vía signal post_save cuando rol.slug == 'estudiante'.
    """
    usuario = models.OneToOneField(
        Usuario, on_delete=models.CASCADE, related_name="perfil_estudiante"
    )
    fecha_nacimiento = models.DateField(null=True, blank=True)
    pais = models.ForeignKey(
        "catalogos.Pais", on_delete=models.SET_NULL, null=True, blank=True
    )
    ciudad = models.ForeignKey(
        "catalogos.Ciudad", on_delete=models.SET_NULL, null=True, blank=True
    )
    biografia = models.TextField(blank=True)
    areas_interes = models.ManyToManyField(
        "catalogos.Categoria", blank=True, related_name="estudiantes_interesados"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Perfil de Estudiante"


class PerfilCertificadora(models.Model):
    """
    Perfil extendido de la institución certificadora.
    Se crea automáticamente vía signal cuando rol.slug == 'certificadora'.
    La certificadora solo puede publicar programas si estado_verificacion.permite_publicar == True.
    """
    usuario = models.OneToOneField(
        Usuario, on_delete=models.CASCADE, related_name="perfil_certificadora"
    )
    nombre_institucion = models.CharField(max_length=255)
    ruc = models.CharField(max_length=20, unique=True, blank=True)
    descripcion = models.TextField(blank=True)
    logo = models.ImageField(upload_to="logos/", null=True, blank=True)
    sitio_web = models.URLField(blank=True)
    pais = models.ForeignKey(
        "catalogos.Pais", on_delete=models.SET_NULL, null=True, blank=True
    )
    ciudad = models.ForeignKey(
        "catalogos.Ciudad", on_delete=models.SET_NULL, null=True, blank=True
    )
    direccion = models.CharField(max_length=255, blank=True)
    estado_verificacion = models.ForeignKey(
        "catalogos.EstadoVerificacion",
        on_delete=models.PROTECT,
        null=True,
        related_name="certificadoras",
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_verificacion = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Perfil de Certificadora"

    def puede_publicar(self):
        return (
            self.estado_verificacion is not None
            and self.estado_verificacion.permite_publicar
        )
```

---

## `programas/models.py`

```python
from django.db import models


class Programa(models.Model):
    """
    Oferta académica publicada por una Certificadora verificada.
    Toda la data clasificatoria referencia modelos de catalogos/.
    """
    # Relaciones principales
    certificadora = models.ForeignKey(
        "usuarios.PerfilCertificadora",
        on_delete=models.CASCADE,
        related_name="programas",
    )
    categoria = models.ForeignKey(
        "catalogos.Categoria",
        on_delete=models.SET_NULL,
        null=True,
        related_name="programas",
    )
    tags = models.ManyToManyField("catalogos.Tag", blank=True, related_name="programas")

    # Catálogos
    tipo = models.ForeignKey(
        "catalogos.TipoPrograma",
        on_delete=models.PROTECT,
        related_name="programas",
    )
    modalidad = models.ForeignKey(
        "catalogos.Modalidad",
        on_delete=models.PROTECT,
        related_name="programas",
    )
    nivel = models.ForeignKey(
        "catalogos.NivelAcademico",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="programas",
    )
    estado = models.ForeignKey(
        "catalogos.EstadoPrograma",
        on_delete=models.PROTECT,
        related_name="programas",
    )
    moneda = models.ForeignKey(
        "catalogos.Moneda",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="programas",
    )

    # Información básica
    titulo = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    descripcion_corta = models.CharField(max_length=300)
    descripcion = models.TextField()
    imagen_portada = models.ImageField(upload_to="programas/", null=True, blank=True)

    # Duración y costo
    duracion_horas = models.PositiveIntegerField(null=True, blank=True)
    duracion_semanas = models.PositiveIntegerField(null=True, blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    es_gratuito = models.BooleanField(default=False)

    # Certificación
    otorga_certificado = models.BooleanField(default=True)
    descripcion_certificado = models.CharField(max_length=255, blank=True)

    # Fechas e inscripción
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    inscripciones_abiertas = models.BooleanField(default=True)
    url_inscripcion = models.URLField(blank=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Programa"
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return self.titulo
```

---

## `postulaciones/models.py`

```python
from django.db import models


class Postulacion(models.Model):
    """
    Interés de un Estudiante en un Programa.
    unique_together evita duplicados.
    """
    estudiante = models.ForeignKey(
        "usuarios.PerfilEstudiante",
        on_delete=models.CASCADE,
        related_name="postulaciones",
    )
    programa = models.ForeignKey(
        "programas.Programa",
        on_delete=models.CASCADE,
        related_name="postulaciones",
    )
    estado = models.ForeignKey(
        "catalogos.EstadoPostulacion",
        on_delete=models.PROTECT,
        related_name="postulaciones",
    )
    mensaje = models.TextField(blank=True)
    fecha_postulacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Postulación"
        unique_together = ("estudiante", "programa")
        ordering = ["-fecha_postulacion"]
```

---

## Data inicial (`fixtures` o `management command`)

Con esta estructura necesitarás poblar los catálogos al desplegar. Los registros mínimos serían:

```python
# catalogos iniciales necesarios para que el sistema funcione
roles = ["Admin (es_publico=False)", "Certificadora", "Estudiante"]
estados_verificacion = ["Pendiente (permite_publicar=False)", "Verificada (permite_publicar=True)", "Suspendida"]
estados_programa = ["Borrador", "Publicado (es_visible_publico=True)", "Pausado", "Archivado"]
estados_postulacion = ["Guardado", "Contactado", "Inscrito (es_estado_final=True)", "Cancelado (es_estado_final=True)"]
tipos_programa = ["Curso", "Diplomado", "Carrera Técnica", "Carrera Universitaria", "Bootcamp", "Certificación"]
modalidades = ["Presencial", "Virtual", "Híbrido"]
niveles = ["Sin requisitos (orden=0)", "Básico (orden=1)", "Intermedio (orden=2)", "Avanzado (orden=3)"]
monedas = ["PEN / S/", "USD / $", "EUR / €"]
```

> **Nota para Claude Code:** crear un `management command` en `catalogos/management/commands/seed_catalogos.py` que inserte estos registros iniciales con `get_or_create` para que sea idempotente y se pueda correr en cualquier entorno.

---

El beneficio clave de este enfoque es que el Admin puede agregar un nuevo tipo de programa, modalidad o estado desde el panel sin necesidad de un nuevo deploy. ¿Seguimos con los serializers o con las signals de creación de perfiles?
