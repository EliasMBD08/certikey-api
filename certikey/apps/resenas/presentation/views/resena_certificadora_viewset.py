from dataclasses import asdict

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from apps.resenas.application.use_cases.create_resena_certificadora import (
    CreateResenaCertificadoraUseCase,
    CreateResenaCertificadoraInput,
)
from apps.resenas.application.use_cases.list_resenas_certificadora import ListResenasCertificadoraUseCase
from apps.resenas.domain.exceptions import ResenaYaExiste, CalificacionInvalida
from apps.resenas.infrastructure.repositories.django_resena_certificadora_repository import DjangoResenaCertificadoraRepository
from apps.resenas.presentation.serializers.resena_certificadora_serializer import CreateResenaCertificadoraSerializer
from apps.usuarios.presentation.permissions import IsEstudiante


def _repo():
    return DjangoResenaCertificadoraRepository()


class ResenaCertificadoraViewSet(ViewSet):
    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        return [IsEstudiante()]

    def list(self, request):
        certificadora_id = request.query_params.get('certificadora_id')
        if not certificadora_id:
            return Response(
                {"detail": "Se requiere el parámetro certificadora_id."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        resenas = ListResenasCertificadoraUseCase(_repo()).execute(int(certificadora_id))
        return Response([asdict(r) for r in resenas])

    def create(self, request):
        serializer = CreateResenaCertificadoraSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        input_dto = CreateResenaCertificadoraInput(
            estudiante_id=request.user.perfil_estudiante.id,
            **serializer.validated_data,
        )
        try:
            resena = CreateResenaCertificadoraUseCase(_repo()).execute(input_dto)
        except ResenaYaExiste as e:
            return Response({"detail": str(e)}, status=status.HTTP_409_CONFLICT)
        except CalificacionInvalida as e:
            return Response({"detail": str(e)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        return Response(asdict(resena), status=status.HTTP_201_CREATED)
