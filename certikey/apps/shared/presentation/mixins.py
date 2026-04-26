from rest_framework import status
from rest_framework.response import Response


class SoftDeleteMixin:
    """
    Mixin para ViewSets que agrega la acción destroy() con soft delete.

    El ViewSet que lo use debe implementar get_instance_for_delete(pk),
    retornando la instancia del modelo o None si no existe / sin acceso.

    Ejemplo de uso:
        class ProgramaViewSet(SoftDeleteMixin, ViewSet):
            def get_instance_for_delete(self, pk):
                try:
                    return Programa.todos.get(pk=pk, certificadora=...)
                except Programa.DoesNotExist:
                    return None

            def destroy(self, request, pk=None):
                return super().destroy(request, pk)
    """

    def get_instance_for_delete(self, pk):
        raise NotImplementedError(
            f"{self.__class__.__name__} debe implementar get_instance_for_delete(pk)."
        )

    def destroy(self, request, pk=None):
        instance = self.get_instance_for_delete(pk)
        if instance is None:
            return Response({"detail": "No encontrado."}, status=status.HTTP_404_NOT_FOUND)
        instance.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
