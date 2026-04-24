from dataclasses import dataclass


@dataclass
class UserEntity:
    id: int
    email: str
    username: str
    first_name: str
    last_name: str
    rol_slug: str | None
    is_active: bool
