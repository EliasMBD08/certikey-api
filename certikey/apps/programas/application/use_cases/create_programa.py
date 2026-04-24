from dataclasses import dataclass, field
from decimal import Decimal

from apps.programas.domain.repositories.programa_repository import AbstractProgramaRepository
from apps.programas.domain.entities.programa import ProgramaEntity
from apps.programas.domain.exceptions import CertificadoraNoVerificada


@dataclass
class CreateProgramaInput:
    certificadora_id: int
    puede_publicar: bool
    titulo: str
    slug: str
    descripcion_corta: str
    descripcion: str
    tipo_id: int
    modalidad_id: int
    es_gratuito: bool
    categoria_id: int | None = None
    nivel_id: int | None = None
    precio: Decimal | None = None
    moneda_id: int | None = None
    duracion_horas: int | None = None
    duracion_semanas: int | None = None
    otorga_certificado: bool = True
    descripcion_certificado: str = ''
    fecha_inicio: str | None = None
    fecha_fin: str | None = None
    inscripciones_abiertas: bool = True
    url_inscripcion: str = ''
    tags_ids: list[int] = field(default_factory=list)


class CreateProgramaUseCase:
    def __init__(self, programa_repository: AbstractProgramaRepository):
        self._repo = programa_repository

    def execute(self, input_dto: CreateProgramaInput) -> ProgramaEntity:
        if not input_dto.puede_publicar:
            raise CertificadoraNoVerificada(
                "La certificadora no está verificada y no puede crear programas."
            )

        kwargs = {k: v for k, v in vars(input_dto).items()
                  if k not in ('certificadora_id', 'puede_publicar')}
        return self._repo.create(certificadora_id=input_dto.certificadora_id, **kwargs)
