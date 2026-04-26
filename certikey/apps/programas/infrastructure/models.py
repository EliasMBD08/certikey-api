from django.db import models

from apps.shared.infrastructure.models import ModeloBase


class Programa(ModeloBase):
    certificadora = models.ForeignKey(
        "usuarios.PerfilCertificadora",
        on_delete=models.CASCADE,
        related_name="programas",
    )
    categoria = models.ForeignKey(
        "catalogos.Categoria",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="programas",
    )
    tags = models.ManyToManyField("catalogos.Tag", blank=True, related_name="programas")
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

    titulo = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    descripcion_corta = models.CharField(max_length=300)
    descripcion = models.TextField()
    imagen_portada = models.ImageField(upload_to="programas/", null=True, blank=True)

    duracion_horas = models.PositiveIntegerField(null=True, blank=True)
    duracion_semanas = models.PositiveIntegerField(null=True, blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    es_gratuito = models.BooleanField(default=False)

    otorga_certificado = models.BooleanField(default=True)
    descripcion_certificado = models.CharField(max_length=255, blank=True)

    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    inscripciones_abiertas = models.BooleanField(default=True)
    url_inscripcion = models.URLField(blank=True)

    class Meta:
        verbose_name = "Programa"
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return self.titulo
