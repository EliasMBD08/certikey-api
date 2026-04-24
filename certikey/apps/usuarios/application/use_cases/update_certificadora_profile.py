from dataclasses import dataclass
from apps.usuarios.domain.repositories.user_repository import AbstractUserRepository
from apps.usuarios.domain.entities.perfil_certificadora import PerfilCertificadoraEntity


@dataclass
class UpdateCertificadoraProfileInput:
    usuario_id: int
    nombre_institucion: str | None = None
    ruc: str | None = None
    descripcion: str | None = None
    sitio_web: str | None = None
    pais_id: int | None = None
    ciudad_id: int | None = None
    direccion: str | None = None


class UpdateCertificadoraProfileUseCase:
    def __init__(self, user_repository: AbstractUserRepository):
        self._repo = user_repository

    def execute(self, input_dto: UpdateCertificadoraProfileInput) -> PerfilCertificadoraEntity:
        kwargs = {k: v for k, v in vars(input_dto).items() if k != 'usuario_id' and v is not None}
        return self._repo.update_perfil_certificadora(input_dto.usuario_id, **kwargs)
