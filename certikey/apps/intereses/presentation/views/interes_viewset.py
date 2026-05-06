from dataclasses import asdict

from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from apps.intereses.application.use_cases.save_interes import SaveInteresUseCase, SaveInteresInput
from apps.intereses.application.use_cases.remove_interes import RemoveInteresUseCase
from apps.intereses.application.use_cases.list_intereses import ListInteresesUseCase
from apps.intereses.application.use_cases.check_interes import CheckInteresUseCase
from apps.intereses.domain.exceptions import InteresYaExiste, InteresNotFound
from apps.intereses.infrastructure.repositories.django_interes_repository import DjangoInteresRepository
from apps.intereses.presentation.serializers.interes_serializer import SaveInteresSerializer
from apps.usuarios.presentation.permissions import IsEstudiante


def _repo():
    return DjangoInteresRepository()


class InteresViewSet(ViewSet):
    permission_classes = [IsEstudiante]

    def list(self, request):
        """GET /api/v1/intereses/ — lista los programas guardados del estudiante."""
        estudiante_id = request.user.perfil_estudiante.id
        intereses = ListInteresesUseCase(_repo()).execute(estudiante_id)
        return Response([asdict(i) for i in intereses])

    def create(self, request):
        """POST /api/v1/intereses/ — guarda un programa de interés."""
        serializer = SaveInteresSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        input_dto = SaveInteresInput(
            estudiante_id=request.user.perfil_estudiante.id,
            programa_id=serializer.validated_data['programa_id'],
        )
        try:
            interes = SaveInteresUseCase(_repo()).execute(input_dto)
        except InteresYaExiste as e:
            return Response({"detail": str(e)}, status=status.HTTP_409_CONFLICT)

        try:
            from apps.programas.infrastructure.models import Programa
            from apps.shared.infrastructure.adapters.http_notification_adapter import HttpNotificationAdapter
            from apps.shared.domain.ports.notification_port import InteresNotificationDTO

            programa = Programa.objects.select_related('certificadora__usuario').get(id=interes.programa_id)
            usuario = request.user
            nombre_estudiante = f"{usuario.first_name} {usuario.last_name}".strip() or usuario.username
            HttpNotificationAdapter().notify_interes(InteresNotificationDTO(
                email_certificadora=programa.certificadora.usuario.email,
                nombre_institucion=programa.certificadora.nombre_institucion,
                nombre_estudiante=nombre_estudiante,
                titulo_programa=programa.titulo,
                programa_id=programa.id,
            ))
        except Exception:
            pass

        return Response(asdict(interes), status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """GET /api/v1/intereses/{programa_id}/ — ¿ya guardé este programa?"""
        estudiante_id = request.user.perfil_estudiante.id
        guardado = CheckInteresUseCase(_repo()).execute(estudiante_id, int(pk))
        return Response({"guardado": guardado})

    def destroy(self, request, pk=None):
        """DELETE /api/v1/intereses/{programa_id}/ — quita el programa de guardados."""
        estudiante_id = request.user.perfil_estudiante.id
        try:
            RemoveInteresUseCase(_repo()).execute(estudiante_id, int(pk))
        except InteresNotFound as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)
