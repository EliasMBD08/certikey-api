from dataclasses import dataclass
from apps.usuarios.domain.repositories.user_repository import AbstractUserRepository
from apps.usuarios.domain.entities.perfil_estudiante import PerfilEstudianteEntity


@dataclass
class UpdateStudentProfileInput:
    usuario_id: int
    fecha_nacimiento: str | None = None
    pais_id: int | None = None
    ciudad_id: int | None = None
    biografia: str | None = None
    areas_interes_ids: list[int] | None = None


class UpdateStudentProfileUseCase:
    def __init__(self, user_repository: AbstractUserRepository):
        self._repo = user_repository

    def execute(self, input_dto: UpdateStudentProfileInput) -> PerfilEstudianteEntity:
        kwargs = {k: v for k, v in vars(input_dto).items() if k != 'usuario_id' and v is not None}
        return self._repo.update_perfil_estudiante(input_dto.usuario_id, **kwargs)
