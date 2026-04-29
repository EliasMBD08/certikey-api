from dataclasses import dataclass
from datetime import datetime


@dataclass
class ResenaCertificadoraEntity:
    id: int
    estudiante_id: int
    certificadora_id: int
    calificacion: int
    comentario: str
    fecha_creacion: datetime
    activo: bool = True
