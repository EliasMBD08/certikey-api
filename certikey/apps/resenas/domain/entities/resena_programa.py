from dataclasses import dataclass
from datetime import datetime


@dataclass
class ResenaProgramaEntity:
    id: int
    estudiante_id: int
    programa_id: int
    calificacion: int
    comentario: str
    fecha_creacion: datetime
    activo: bool = True
