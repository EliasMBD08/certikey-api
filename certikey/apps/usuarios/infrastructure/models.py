from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
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
