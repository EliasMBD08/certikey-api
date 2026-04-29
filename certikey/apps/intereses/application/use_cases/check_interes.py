from apps.intereses.domain.repositories.interes_repository import AbstractInteresRepository


class CheckInteresUseCase:
    def __init__(self, repository: AbstractInteresRepository):
        self._repo = repository

    def execute(self, estudiante_id: int, programa_id: int) -> bool:
        existing = self._repo.get(estudiante_id, programa_id)
        return existing is not None and existing.activo
