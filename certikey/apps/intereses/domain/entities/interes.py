from dataclasses import dataclass
from datetime import datetime


@dataclass
class InteresEntity:
    id: int
    estudiante_id: int
    programa_id: int
    fecha_creacion: datetime
    activo: bool = True
