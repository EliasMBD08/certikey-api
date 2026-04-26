from django.db import models


class SoftDeleteQuerySet(models.QuerySet):
    def activos(self):
        return self.filter(activo=True)

    def inactivos(self):
        return self.filter(activo=False)

    def soft_delete(self):
        return self.update(activo=False)

    def restore(self):
        return self.update(activo=True)


class SoftDeleteManager(models.Manager):
    """Manager por defecto: solo retorna registros con activo=True."""

    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).filter(activo=True)


class ModeloBase(models.Model):
    """
    Clase base abstracta para todos los modelos del dominio.

    Provee:
    - fecha_creacion / fecha_actualizacion — timestamps automáticos.
    - activo — flag para soft delete.
    - objects  — manager filtrado (solo activos).
    - todos    — manager sin filtro (activos e inactivos).
    """

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True, db_index=True)

    objects = SoftDeleteManager()
    todos = models.Manager()

    class Meta:
        abstract = True

    def soft_delete(self):
        self.activo = False
        self.save(update_fields=["activo", "fecha_actualizacion"])

    def restore(self):
        self.activo = True
        self.save(update_fields=["activo", "fecha_actualizacion"])
