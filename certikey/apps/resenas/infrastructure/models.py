from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from apps.shared.infrastructure.models import ModeloBase


class ResenaPrograma(ModeloBase):
    estudiante = models.ForeignKey(
        "usuarios.PerfilEstudiante",
        on_delete=models.CASCADE,
        related_name="resenas_programas",
    )
    programa = models.ForeignKey(
        "programas.Programa",
        on_delete=models.CASCADE,
        related_name="resenas",
    )
    calificacion = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comentario = models.TextField()

    class Meta:
        verbose_name = "Reseña de Programa"
        verbose_name_plural = "Reseñas de Programas"
        unique_together = ("estudiante", "programa")
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return f"Reseña de estudiante {self.estudiante_id} en programa {self.programa_id} ({self.calificacion}/5)"


class ResenaCertificadora(ModeloBase):
    estudiante = models.ForeignKey(
        "usuarios.PerfilEstudiante",
        on_delete=models.CASCADE,
        related_name="resenas_certificadoras",
    )
    certificadora = models.ForeignKey(
        "usuarios.PerfilCertificadora",
        on_delete=models.CASCADE,
        related_name="resenas",
    )
    calificacion = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comentario = models.TextField()

    class Meta:
        verbose_name = "Reseña de Certificadora"
        verbose_name_plural = "Reseñas de Certificadoras"
        unique_together = ("estudiante", "certificadora")
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return f"Reseña de estudiante {self.estudiante_id} en certificadora {self.certificadora_id} ({self.calificacion}/5)"
