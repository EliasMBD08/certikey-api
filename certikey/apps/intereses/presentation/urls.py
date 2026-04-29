from rest_framework.routers import DefaultRouter

from apps.intereses.presentation.views.interes_viewset import InteresViewSet

router = DefaultRouter()
router.register(r'intereses', InteresViewSet, basename='interes')

urlpatterns = router.urls
