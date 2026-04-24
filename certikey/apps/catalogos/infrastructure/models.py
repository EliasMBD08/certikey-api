from django.db import models


class Pais(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    codigo_iso = models.CharField(max_length=3, unique=True)

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
    nombre = models.CharField(max_length=50)
    codigo_iso = models.CharField(max_length=5, unique=True)
    simbolo = models.CharField(max_length=5)

    class Meta:
        verbose_name = "Moneda"

    def __str__(self):
        return f"{self.codigo_iso} ({self.simbolo})"


class Rol(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    descripcion = models.CharField(max_length=255, blank=True)
    es_publico = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Rol"

    def __str__(self):
        return self.nombre


class TipoPrograma(models.Model):
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
    nombre = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    descripcion = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Modalidad"

    def __str__(self):
        return self.nombre


class NivelAcademico(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    orden = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = "Nivel Académico"
        ordering = ["orden"]

    def __str__(self):
        return self.nombre


class EstadoPrograma(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    descripcion = models.CharField(max_length=255, blank=True)
    es_visible_publico = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Estado de Programa"

    def __str__(self):
        return self.nombre


class EstadoVerificacion(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    permite_publicar = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Estado de Verificación"

    def __str__(self):
        return self.nombre


class EstadoPostulacion(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    descripcion = models.CharField(max_length=255, blank=True)
    es_estado_final = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Estado de Postulación"

    def __str__(self):
        return self.nombre


class Categoria(models.Model):
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
    nombre = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.nombre
