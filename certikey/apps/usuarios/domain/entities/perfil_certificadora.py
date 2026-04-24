from dataclasses import dataclass


@dataclass
class PerfilCertificadoraEntity:
    id: int
    usuario_id: int
    nombre_institucion: str
    ruc: str
    descripcion: str
    sitio_web: str
    pais_id: int | None
    ciudad_id: int | None
    direccion: str
    estado_verificacion_slug: str | None
    puede_publicar: bool
