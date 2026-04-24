from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from dataclasses import asdict

from apps.usuarios.application.use_cases.get_profile import GetProfileUseCase
from apps.usuarios.application.use_cases.update_student_profile import (
    UpdateStudentProfileUseCase, UpdateStudentProfileInput,
)
from apps.usuarios.application.use_cases.update_certificadora_profile import (
    UpdateCertificadoraProfileUseCase, UpdateCertificadoraProfileInput,
)
from apps.usuarios.infrastructure.repositories.django_user_repository import DjangoUserRepository
from apps.usuarios.presentation.serializers.profile_serializer import (
    PerfilEstudianteSerializer, PerfilCertificadoraSerializer,
)
from apps.usuarios.domain.exceptions import PerfilNotFound


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_repo(self):
        return DjangoUserRepository()

    def get(self, request):
        use_case = GetProfileUseCase(user_repository=self._get_repo())
        user, perfil = use_case.execute(request.user.id)

        user_data = {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "rol": user.rol_slug,
        }

        if perfil is None:
            return Response({"usuario": user_data, "perfil": None})

        if user.rol_slug == 'estudiante':
            perfil_data = PerfilEstudianteSerializer(asdict(perfil)).data
        else:
            perfil_data = PerfilCertificadoraSerializer(asdict(perfil)).data

        return Response({"usuario": user_data, "perfil": perfil_data})

    def patch(self, request):
        repo = self._get_repo()
        user_id = request.user.id

        try:
            if request.user.es_estudiante():
                serializer = PerfilEstudianteSerializer(data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                input_dto = UpdateStudentProfileInput(usuario_id=user_id, **serializer.validated_data)
                perfil = UpdateStudentProfileUseCase(repo).execute(input_dto)
                return Response(PerfilEstudianteSerializer(asdict(perfil)).data)

            elif request.user.es_certificadora():
                serializer = PerfilCertificadoraSerializer(data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                input_dto = UpdateCertificadoraProfileInput(usuario_id=user_id, **serializer.validated_data)
                perfil = UpdateCertificadoraProfileUseCase(repo).execute(input_dto)
                return Response(PerfilCertificadoraSerializer(asdict(perfil)).data)

            return Response({"detail": "Rol sin perfil editable."}, status=status.HTTP_400_BAD_REQUEST)

        except PerfilNotFound as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
