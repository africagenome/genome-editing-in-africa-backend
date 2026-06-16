# api/v1/urls.py (Modular version)

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# Import routers from individual modules
from core.urls import router as core_router
from users.urls import router as users_router

# Swagger schema view
schema_view = get_schema_view(
    openapi.Info(
        title="AUDA-NEPAD Genome Editing API",
        default_version='v1',
        description="API for Genome Editing in Africa Portal",
        terms_of_service="https://www.nepad.org/terms",
        contact=openapi.Contact(email="genome@nepad.org"),
        license=openapi.License(name="AUDA-NEPAD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# Combine routers
router = DefaultRouter()
router.registry.extend(core_router.registry)
router.registry.extend(users_router.registry)

urlpatterns = [
    # Main API
    path('', include(router.urls)),
    
    # Authentication
    path('auth/', include('users.auth_urls')),
    
    # JWT
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # Newsletter
    path('newsletter/', include('users.newsletter_urls')),
    
    # Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]