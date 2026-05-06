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

        try:
            from apps.programas.infrastructure.models import Programa
            from apps.shared.infrastructure.adapters.http_notification_adapter import HttpNotificationAdapter
            from apps.shared.domain.ports.notification_port import ResenaNotificationDTO

            programa = Programa.objects.select_related('certificadora__usuario').get(id=resena.programa_id)
            usuario = request.user
            nombre_estudiante = f"{usuario.first_name} {usuario.last_name}".strip() or usuario.username
            HttpNotificationAdapter().notify_resena(ResenaNotificationDTO(
                email_certificadora=programa.certificadora.usuario.email,
                nombre_institucion=programa.certificadora.nombre_institucion,
                nombre_estudiante=nombre_estudiante,
                titulo_programa=programa.titulo,
                programa_id=programa.id,
                calificacion=resena.calificacion,
                comentario=resena.comentario,
            ))
        except Exception:
            pass

        return Response(asdict(resena), status=status.HTTP_201_CREATED)
