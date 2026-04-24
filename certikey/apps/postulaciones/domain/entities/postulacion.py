from dataclasses import dataclass
from datetime import datetime


@dataclass
class PostulacionEntity:
    id: int
    estudiante_id: int
    programa_id: int
    estado_slug: str
    mensaje: str
    fecha_postulacion: datetime
