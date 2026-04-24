from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender='usuarios.Usuario')
def crear_perfil_usuario(sender, instance, created, **kwargs):
    if not created or not instance.rol:
        return

    if instance.rol.slug == 'estudiante':
        from apps.usuarios.infrastructure.models import PerfilEstudiante
        PerfilEstudiante.objects.get_or_create(usuario=instance)

    elif instance.rol.slug == 'certificadora':
        from apps.usuarios.infrastructure.models import PerfilCertificadora
        from apps.catalogos.infrastructure.models import EstadoVerificacion
        estado_pendiente = EstadoVerificacion.objects.filter(slug='pendiente').first()
        PerfilCertificadora.objects.get_or_create(
            usuario=instance,
            defaults={
                'nombre_institucion': instance.get_full_name() or instance.username,
                'estado_verificacion': estado_pendiente,
            },
        )
