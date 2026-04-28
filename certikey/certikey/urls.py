from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    # Auth
    path('api/v1/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/auth/', include('apps.usuarios.presentation.auth_urls')),
    # Resources
    path('api/v1/catalogos/', include('apps.catalogos.presentation.urls')),
    path('api/v1/usuarios/', include('apps.usuarios.presentation.usuario_urls')),
    path('api/v1/', include('apps.programas.presentation.urls')),
    path('api/v1/', include('apps.postulaciones.presentation.urls')),
    path('api/v1/', include('apps.resenas.presentation.urls')),
    # Docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
