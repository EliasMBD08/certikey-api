from dataclasses import dataclass
from apps.usuarios.domain.repositories.user_repository import AbstractUserRepository
from apps.usuarios.domain.exceptions import EmailAlreadyExists


@dataclass
class RegisterUserInput:
    email: str
    username: str
    password: str
    first_name: str
    last_name: str
    rol_slug: str


@dataclass
class RegisterUserOutput:
    id: int
    email: str
    username: str
    rol_slug: str | None


class RegisterUserUseCase:
    def __init__(self, user_repository: AbstractUserRepository):
        self._repo = user_repository

    def execute(self, input_dto: RegisterUserInput) -> RegisterUserOutput:
        if self._repo.email_exists(input_dto.email):
            raise EmailAlreadyExists(f"El email '{input_dto.email}' ya está registrado.")

        user = self._repo.create(
            email=input_dto.email,
            username=input_dto.username,
            password=input_dto.password,
            first_name=input_dto.first_name,
            last_name=input_dto.last_name,
            rol_slug=input_dto.rol_slug,
        )
        return RegisterUserOutput(id=user.id, email=user.email, username=user.username, rol_slug=user.rol_slug)
