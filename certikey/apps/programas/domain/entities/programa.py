from dataclasses import dataclass, field
from datetime import datetime, date
from decimal import Decimal


@dataclass
class ProgramaEntity:
    id: int
    titulo: str
    slug: str
    descripcion_corta: str
    descripcion: str
    certificadora_id: int
    tipo_id: int
    modalidad_id: int
    estado_slug: str
    es_gratuito: bool
    inscripciones_abiertas: bool
    fecha_creacion: datetime
    categoria_id: int | None = None
    nivel_id: int | None = None
    precio: Decimal | None = None
    moneda_id: int | None = None
    duracion_horas: int | None = None
    duracion_semanas: int | None = None
    otorga_certificado: bool = True
    descripcion_certificado: str = ''
    fecha_inicio: date | None = None
    fecha_fin: date | None = None
    url_inscripcion: str = ''
    tags_ids: list[int] = field(default_factory=list)
