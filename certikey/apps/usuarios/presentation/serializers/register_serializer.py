from rest_framework import serializers


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(min_length=8, write_only=True)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    rol_slug = serializers.CharField(required=False, allow_null=True)

    def validate_rol_slug(self, value):
        if value:
            from apps.catalogos.infrastructure.models import Rol
            if not Rol.objects.filter(slug=value, es_publico=True).exists():
                raise serializers.ValidationError(f"El rol '{value}' no es válido para registro.")
        return value
