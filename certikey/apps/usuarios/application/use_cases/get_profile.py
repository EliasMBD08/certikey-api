from apps.usuarios.domain.repositories.user_repository import AbstractUserRepository
from apps.usuarios.domain.entities.user import UserEntity
from apps.usuarios.domain.entities.perfil_estudiante import PerfilEstudianteEntity
from apps.usuarios.domain.entities.perfil_certificadora import PerfilCertificadoraEntity
from apps.usuarios.domain.exceptions import UserNotFound


class GetProfileUseCase:
    def __init__(self, user_repository: AbstractUserRepository):
        self._repo = user_repository

    def execute(self, user_id: int) -> tuple[UserEntity, PerfilEstudianteEntity | PerfilCertificadoraEntity | None]:
        user = self._repo.get_by_id(user_id)
        perfil = None
        if user.rol_slug == 'estudiante':
            perfil = self._repo.get_perfil_estudiante(user_id)
        elif user.rol_slug == 'certificadora':
            perfil = self._repo.get_perfil_certificadora(user_id)
        return user, perfil
