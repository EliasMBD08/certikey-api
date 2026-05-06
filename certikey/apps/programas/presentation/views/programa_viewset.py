from dataclasses import asdict
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status

from apps.programas.application.use_cases.create_programa import CreateProgramaUseCase, CreateProgramaInput
from apps.programas.application.use_cases.list_programas import ListProgramasUseCase
from apps.programas.application.use_cases.get_programa import GetProgramaUseCase
from apps.programas.application.use_cases.update_programa import UpdateProgramaUseCase, UpdateProgramaInput
from apps.programas.application.use_cases.publish_programa import PublishProgramaUseCase
from apps.programas.infrastructure.repositories.django_programa_repository import DjangoProgramaRepository
from apps.programas.presentation.serializers.programa_serializer import ProgramaSerializer, ProgramaUpdateSerializer
from apps.programas.domain.exceptions import (
    ProgramaNotFound, CertificadoraNoVerificada, ProgramaYaPublicado, AccesoDenegado, CategoriasExcedidas,
)
from apps.usuarios.presentation.permissions import IsCertificadora


def _repo():
    return DjangoProgramaRepository()


class ProgramaViewSet(ViewSet):
    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [AllowAny()]
        return [IsCertificadora()]

    def list(self, request):
        filters = {
            'categorias': request.query_params.getlist('categorias'),
            'tipo': request.query_params.get('tipo'),
            'modalidad': request.query_params.get('modalidad'),
            'nivel': request.query_params.get('nivel'),
            'es_gratuito': _parse_bool(request.query_params.get('es_gratuito')),
            'inscripciones_abiertas': _parse_bool(request.query_params.get('inscripciones_abiertas')),
            'precio_max': request.query_params.get('precio_max'),
            'search': request.query_params.get('search'),
        }
        programas = ListProgramasUseCase(_repo()).execute(filters)
        return Response([asdict(p) for p in programas])

    def retrieve(self, request, pk=None):
        try:
            programa = GetProgramaUseCase(_repo()).execute(int(pk))
        except ProgramaNotFound as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
        return Response(asdict(programa))

    def create(self, request):
        serializer = ProgramaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        perfil = request.user.perfil_certificadora
        input_dto = CreateProgramaInput(
            certificadora_id=perfil.id,
            puede_publicar=perfil.puede_publicar(),
            **serializer.validated_data,
        )
        try:
            programa = CreateProgramaUseCase(_repo()).execute(input_dto)
        except CertificadoraNoVerificada as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except CategoriasExcedidas as e:
            return Response({"detail": str(e)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        return Response(asdict(programa), status=status.HTTP_201_CREATED)

    def partial_update(self, request, pk=None):
        serializer = ProgramaUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        perfil = request.user.perfil_certificadora
        programa_antes = GetProgramaUseCase(_repo()).execute(int(pk))

        input_dto = UpdateProgramaInput(
            programa_id=int(pk),
            certificadora_id=perfil.id,
            **serializer.validated_data,
        )
        try:
            programa = UpdateProgramaUseCase(_repo()).execute(input_dto)
        except ProgramaNotFound as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except AccesoDenegado as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except CategoriasExcedidas as e:
            return Response({"detail": str(e)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        activado_gratuito = (
            not programa_antes.es_gratuito
            and programa.es_gratuito
            and programa.otorga_certificado
        )
        if activado_gratuito:
            try:
                from apps.intereses.infrastructure.models import Interes
                from apps.shared.infrastructure.adapters.http_notification_adapter import HttpNotificationAdapter
                from apps.shared.domain.ports.notification_port import ProgramaGratuitoNotificationDTO

                emails = list(
                    Interes.objects.filter(programa_id=programa.id)
                    .select_related('estudiante__usuario')
                    .values_list('estudiante__usuario__email', flat=True)
                )
                if emails:
                    HttpNotificationAdapter().notify_programa_gratuito(ProgramaGratuitoNotificationDTO(
                        titulo_programa=programa.titulo,
                        programa_id=programa.id,
                        emails_estudiantes=emails,
                    ))
            except Exception:
                pass

        return Response(asdict(programa))

    @action(detail=True, methods=['post'], url_path='publicar')
    def publicar(self, request, pk=None):
        perfil = request.user.perfil_certificadora
        try:
            programa = PublishProgramaUseCase(_repo()).execute(
                programa_id=int(pk),
                certificadora_id=perfil.id,
                puede_publicar=perfil.puede_publicar(),
            )
        except ProgramaNotFound as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except AccesoDenegado as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except CertificadoraNoVerificada as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ProgramaYaPublicado as e:
            return Response({"detail": str(e)}, status=status.HTTP_409_CONFLICT)

        return Response(asdict(programa))


def _parse_bool(value):
    if value is None:
        return None
    return value.lower() in ('true', '1', 'yes')
