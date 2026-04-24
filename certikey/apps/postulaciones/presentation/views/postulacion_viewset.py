from dataclasses import asdict
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status

from apps.postulaciones.application.use_cases.create_postulacion import (
    CreatePostulacionUseCase, CreatePostulacionInput,
)
from apps.postulaciones.application.use_cases.list_postulaciones import ListPostulacionesUseCase
from apps.postulaciones.infrastructure.repositories.django_postulacion_repository import DjangoPostulacionRepository
from apps.programas.infrastructure.repositories.django_programa_repository import DjangoProgramaRepository
from apps.postulaciones.presentation.serializers.postulacion_serializer import (
    CreatePostulacionSerializer, PostulacionSerializer,
)
from apps.postulaciones.domain.exceptions import (
    PostulacionDuplicada, ProgramaSinInscripciones, PostulacionNotFound, AccesoDenegado,
)
from apps.usuarios.presentation.permissions import IsEstudiante


def _repo():
    return DjangoPostulacionRepository()


class PostulacionViewSet(ViewSet):
    permission_classes = [IsEstudiante]

    def _get_estudiante_id(self, request):
        return request.user.perfil_estudiante.id

    def list(self, request):
        estudiante_id = self._get_estudiante_id(request)
        postulaciones = ListPostulacionesUseCase(_repo()).execute(estudiante_id)
        return Response([asdict(p) for p in postulaciones])

    def create(self, request):
        serializer = CreatePostulacionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        estudiante_id = self._get_estudiante_id(request)
        input_dto = CreatePostulacionInput(
            estudiante_id=estudiante_id,
            **serializer.validated_data,
        )
        use_case = CreatePostulacionUseCase(
            postulacion_repository=_repo(),
            programa_repository=DjangoProgramaRepository(),
        )
        try:
            postulacion = use_case.execute(input_dto)
        except PostulacionDuplicada as e:
            return Response({"detail": str(e)}, status=status.HTTP_409_CONFLICT)
        except ProgramaSinInscripciones as e:
            return Response({"detail": str(e)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        return Response(asdict(postulacion), status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        try:
            postulacion = _repo().get_by_id(int(pk))
        except PostulacionNotFound as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

        if postulacion.estudiante_id != self._get_estudiante_id(request):
            return Response({"detail": "No tienes acceso a esta postulación."}, status=status.HTTP_403_FORBIDDEN)

        return Response(asdict(postulacion))
