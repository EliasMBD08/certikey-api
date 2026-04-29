from rest_framework import serializers


class SaveInteresSerializer(serializers.Serializer):
    programa_id = serializers.IntegerField()


class InteresSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    estudiante_id = serializers.IntegerField(read_only=True)
    programa_id = serializers.IntegerField(read_only=True)
    fecha_creacion = serializers.DateTimeField(read_only=True)
