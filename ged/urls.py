from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


admin.site.site_header = "AUDA-NEPAD Africa Gene Editing Portal"
admin.site.site_title = "AUDA-NEPAD Africa Gene Editing Portal"
admin.site.index_title = "Welcome to the AUDA-NEPAD Africa Gene Editing Portal"

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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('api/auth/', include('users.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)