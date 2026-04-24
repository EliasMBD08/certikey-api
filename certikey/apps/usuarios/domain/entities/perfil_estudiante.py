from dataclasses import dataclass, field
from datetime import date


@dataclass
class PerfilEstudianteEntity:
    id: int
    usuario_id: int
    fecha_nacimiento: date | None
    pais_id: int | None
    ciudad_id: int | None
    biografia: str
    areas_interes_ids: list[int] = field(default_factory=list)
