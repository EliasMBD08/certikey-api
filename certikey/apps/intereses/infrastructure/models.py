from django.db import models

from apps.shared.infrastructure.models import ModeloBase


class Interes(ModeloBase):
    estudiante = models.ForeignKey(
        "usuarios.PerfilEstudiante",
        on_delete=models.CASCADE,
        related_name="intereses",
    )
    programa = models.ForeignKey(
        "programas.Programa",
        on_delete=models.CASCADE,
        related_name="interesados",
    )

    class Meta:
        verbose_name = "Interés"
        verbose_name_plural = "Intereses"
        unique_together = ("estudiante", "programa")
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return f"Interés de estudiante {self.estudiante_id} en programa {self.programa_id}"
