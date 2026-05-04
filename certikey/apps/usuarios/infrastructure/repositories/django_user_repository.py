from django.db import transaction, IntegrityError

from apps.usuarios.domain.repositories.user_repository import AbstractUserRepository
from apps.usuarios.domain.entities.user import UserEntity
from apps.usuarios.domain.entities.perfil_estudiante import PerfilEstudianteEntity
from apps.usuarios.domain.entities.perfil_certificadora import PerfilCertificadoraEntity
from apps.usuarios.domain.exceptions import RolNotFound, InvalidRole, UserNotFound, PerfilNotFound, EmailAlreadyExists


class DjangoUserRepository(AbstractUserRepository):
    @transaction.atomic
    def create(self, email, username, password, first_name, last_name, rol_slug):
        from apps.usuarios.infrastructure.models import Usuario
        from apps.catalogos.infrastructure.models import Rol

        try:
            rol = Rol.objects.get(slug=rol_slug)
        except Rol.DoesNotExist:
            raise RolNotFound(f"El rol '{rol_slug}' no existe.")

        if not rol.es_publico:
            raise InvalidRole(f"El rol '{rol_slug}' no está disponible para registro.")

        try:
            user = Usuario.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                rol=rol,
            )
        except IntegrityError:
            raise EmailAlreadyExists(f"El email '{email}' ya está registrado.")
        return self._user_to_entity(user)

    def get_by_id(self, user_id):
        from apps.usuarios.infrastructure.models import Usuario
        try:
            user = Usuario.objects.select_related('rol').get(id=user_id)
        except Usuario.DoesNotExist:
            raise UserNotFound(f"Usuario {user_id} no encontrado.")
        return self._user_to_entity(user)

    def email_exists(self, email):
        from apps.usuarios.infrastructure.models import Usuario
        return Usuario.objects.filter(email=email).exists()

    def get_perfil_estudiante(self, usuario_id):
        from apps.usuarios.infrastructure.models import PerfilEstudiante
        try:
            perfil = PerfilEstudiante.objects.prefetch_related('areas_interes').get(usuario_id=usuario_id)
        except PerfilEstudiante.DoesNotExist:
            raise PerfilNotFound(f"Perfil de estudiante para usuario {usuario_id} no encontrado.")
        return self._estudiante_to_entity(perfil)

    def get_perfil_certificadora(self, usuario_id):
        from apps.usuarios.infrastructure.models import PerfilCertificadora
        try:
            perfil = PerfilCertificadora.objects.select_related('estado_verificacion').get(usuario_id=usuario_id)
        except PerfilCertificadora.DoesNotExist:
            raise PerfilNotFound(f"Perfil de certificadora para usuario {usuario_id} no encontrado.")
        return self._certificadora_to_entity(perfil)

    @transaction.atomic
    def update_perfil_estudiante(self, usuario_id, **kwargs):
        from apps.usuarios.infrastructure.models import PerfilEstudiante
        areas_interes_ids = kwargs.pop('areas_interes_ids', None)
        perfil = PerfilEstudiante.objects.get(usuario_id=usuario_id)
        for field, value in kwargs.items():
            setattr(perfil, field, value)
        perfil.save()
        if areas_interes_ids is not None:
            perfil.areas_interes.set(areas_interes_ids)
        return self._estudiante_to_entity(perfil)

    def update_perfil_certificadora(self, usuario_id, **kwargs):
        from apps.usuarios.infrastructure.models import PerfilCertificadora
        perfil = PerfilCertificadora.objects.get(usuario_id=usuario_id)
        for field, value in kwargs.items():
            setattr(perfil, field, value)
        perfil.save()
        return self._certificadora_to_entity(perfil)

    def _user_to_entity(self, user) -> UserEntity:
        return UserEntity(
            id=user.id,
            email=user.email,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            rol_slug=user.rol.slug if user.rol else None,
            is_active=user.is_active,
        )

    def _estudiante_to_entity(self, perfil) -> PerfilEstudianteEntity:
        return PerfilEstudianteEntity(
            id=perfil.id,
            usuario_id=perfil.usuario_id,
            fecha_nacimiento=perfil.fecha_nacimiento,
            pais_id=perfil.pais_id,
            ciudad_id=perfil.ciudad_id,
            biografia=perfil.biografia,
            areas_interes_ids=list(perfil.areas_interes.values_list('id', flat=True)),
        )

    def _certificadora_to_entity(self, perfil) -> PerfilCertificadoraEntity:
        return PerfilCertificadoraEntity(
            id=perfil.id,
            usuario_id=perfil.usuario_id,
            nombre_institucion=perfil.nombre_institucion,
            ruc=perfil.ruc,
            descripcion=perfil.descripcion,
            sitio_web=perfil.sitio_web,
            pais_id=perfil.pais_id,
            ciudad_id=perfil.ciudad_id,
            direccion=perfil.direccion,
            estado_verificacion_slug=perfil.estado_verificacion.slug if perfil.estado_verificacion else None,
            puede_publicar=perfil.puede_publicar(),
        )
