from rest_framework.routers import DefaultRouter
from apps.catalogos.presentation.views import (
    PaisViewSet, CiudadViewSet, MonedaViewSet, RolViewSet,
    TipoProgramaViewSet, ModalidadViewSet, NivelAcademicoViewSet,
    CategoriaViewSet, TagViewSet,
)

router = DefaultRouter()
router.register(r'paises', PaisViewSet, basename='pais')
router.register(r'ciudades', CiudadViewSet, basename='ciudad')
router.register(r'monedas', MonedaViewSet, basename='moneda')
router.register(r'roles', RolViewSet, basename='rol')
router.register(r'tipos-programa', TipoProgramaViewSet, basename='tipo-programa')
router.register(r'modalidades', ModalidadViewSet, basename='modalidad')
router.register(r'niveles', NivelAcademicoViewSet, basename='nivel')
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'tags', TagViewSet, basename='tag')

urlpatterns = router.urls
