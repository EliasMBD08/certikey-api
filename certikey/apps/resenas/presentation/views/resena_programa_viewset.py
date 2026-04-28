from dataclasses import asdict

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from apps.resenas.application.use_cases.create_resena_programa import (
    CreateResenaProgramaUseCase,
    CreateResenaProgramaInput,
)
from apps.resenas.application.use_cases.list_resenas_programa import ListResenasProgramaUseCase
from apps.resenas.domain.exceptions import ResenaYaExiste, CalificacionInvalida
from apps.resenas.infrastructure.repositories.django_resena_programa_repository import DjangoResenaProgramaRepository
from apps.resenas.presentation.serializers.resena_programa_serializer import CreateResenaProgramaSerializer
from apps.usuarios.presentation.permissions import IsEstudiante


def _repo():
    return DjangoResenaProgramaRepository()


class ResenaProgramaViewSet(ViewSet):
    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        return [IsEstudiante()]

    def list(self, request):
        programa_id = request.query_params.get('programa_id')
        if not programa_id:
            return Response(
                {"detail": "Se requiere el parámetro programa_id."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        resenas = ListResenasProgramaUseCase(_repo()).execute(int(programa_id))
        return Response([asdict(r) for r in resenas])

    def create(self, request):
        serializer = CreateResenaProgramaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        input_dto = CreateResenaProgramaInput(
            estudiante_id=request.user.perfil_estudiante.id,
            **serializer.validated_data,
        )
        try:
            resena = CreateResenaProgramaUseCase(_repo()).execute(input_dto)
        except ResenaYaExiste as e:
            return Response({"detail": str(e)}, status=status.HTTP_409_CONFLICT)
        except CalificacionInvalida as e:
            return Response({"detail": str(e)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        return Response(asdict(resena), status=status.HTTP_201_CREATED)
