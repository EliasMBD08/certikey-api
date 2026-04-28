from dataclasses import dataclass
from apps.programas.domain.repositories.programa_repository import AbstractProgramaRepository
from apps.programas.domain.entities.programa import ProgramaEntity
from apps.programas.domain.exceptions import ProgramaNotFound, AccesoDenegado, CategoriasExcedidas

MAX_CATEGORIAS = 5


@dataclass
class UpdateProgramaInput:
    programa_id: int
    certificadora_id: int
    titulo: str | None = None
    descripcion_corta: str | None = None
    descripcion: str | None = None
    precio: float | None = None
    es_gratuito: bool | None = None
    inscripciones_abiertas: bool | None = None
    categorias_ids: list[int] | None = None
    nivel_id: int | None = None
    moneda_id: int | None = None
    duracion_horas: int | None = None
    duracion_semanas: int | None = None
    fecha_inicio: str | None = None
    fecha_fin: str | None = None
    url_inscripcion: str | None = None
    tags_ids: list[int] | None = None


class UpdateProgramaUseCase:
    def __init__(self, programa_repository: AbstractProgramaRepository):
        self._repo = programa_repository

    def execute(self, input_dto: UpdateProgramaInput) -> ProgramaEntity:
        programa = self._repo.get_by_id(input_dto.programa_id)

        if programa.certificadora_id != input_dto.certificadora_id:
            raise AccesoDenegado("No tienes permiso para editar este programa.")

        if input_dto.categorias_ids is not None and len(input_dto.categorias_ids) > MAX_CATEGORIAS:
            raise CategoriasExcedidas(
                f"Un programa no puede tener más de {MAX_CATEGORIAS} categorías."
            )

        kwargs = {
            k: v for k, v in vars(input_dto).items()
            if k not in ('programa_id', 'certificadora_id') and v is not None
        }
        return self._repo.update(input_dto.programa_id, **kwargs)
