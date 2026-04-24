from abc import ABC, abstractmethod
from apps.usuarios.domain.entities.user import UserEntity
from apps.usuarios.domain.entities.perfil_estudiante import PerfilEstudianteEntity
from apps.usuarios.domain.entities.perfil_certificadora import PerfilCertificadoraEntity


class AbstractUserRepository(ABC):
    @abstractmethod
    def create(
        self,
        email: str,
        username: str,
        password: str,
        first_name: str,
        last_name: str,
        rol_slug: str,
    ) -> UserEntity: ...

    @abstractmethod
    def get_by_id(self, user_id: int) -> UserEntity: ...

    @abstractmethod
    def email_exists(self, email: str) -> bool: ...

    @abstractmethod
    def get_perfil_estudiante(self, usuario_id: int) -> PerfilEstudianteEntity: ...

    @abstractmethod
    def get_perfil_certificadora(self, usuario_id: int) -> PerfilCertificadoraEntity: ...

    @abstractmethod
    def update_perfil_estudiante(self, usuario_id: int, **kwargs) -> PerfilEstudianteEntity: ...

    @abstractmethod
    def update_perfil_certificadora(self, usuario_id: int, **kwargs) -> PerfilCertificadoraEntity: ...
