from django.db import models


class Postulacion(models.Model):
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
