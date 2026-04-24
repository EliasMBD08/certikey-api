from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer
from rest_framework import serializers as drf_serializers

from apps.usuarios.presentation.serializers.register_serializer import RegisterSerializer
from apps.usuarios.application.use_cases.register_user import RegisterUserUseCase, RegisterUserInput
from apps.usuarios.infrastructure.repositories.django_user_repository import DjangoUserRepository
from apps.usuarios.domain.exceptions import EmailAlreadyExists, RolNotFound, InvalidRole


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Registrar nuevo usuario",
        request=RegisterSerializer,
        responses={
            201: inline_serializer(
                name="RegisterResponse",
                fields={
                    "email": drf_serializers.EmailField(),
                    "username": drf_serializers.CharField(),
                    "password": drf_serializers.CharField(),
                    "first_name": drf_serializers.CharField(),
                    "last_name": drf_serializers.IntegerField()
                },
            ),
            400: OpenApiResponse(description="Datos inválidos o rol no encontrado"),
            409: OpenApiResponse(description="El email ya está registrado"),
        },
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        input_dto = RegisterUserInput(**serializer.validated_data)
        use_case = RegisterUserUseCase(user_repository=DjangoUserRepository())

        try:
            output = use_case.execute(input_dto)
        except EmailAlreadyExists as e:
            return Response({"detail": str(e)}, status=status.HTTP_409_CONFLICT)
        except (RolNotFound, InvalidRole) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"id": output.id, "email": output.email, "username": output.username, "rol": output.rol_slug},
            status=status.HTTP_201_CREATED,
        )
