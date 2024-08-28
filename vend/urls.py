from django.urls import path, include
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views as rest_framework_view
from rest_framework_bulk.routes import BulkRouter
from redemption_code import views as redemption_code_views
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

router = DefaultRouter()
router.register(r'applications', redemption_code_views.ApplicationViewSet)
router.register(r'redemption-codes', redemption_code_views.RedemptionCodeViewSet)

schema_view = get_schema_view(
   openapi.Info(
      title="兑换码 API",
      default_version='v1',
      description="兑换码系统的 API 文档",
      terms_of_service="https://www.yourapp.com/terms/",
      contact=openapi.Contact(email="contact@yourapp.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    path('api-token-auth/', rest_framework_view.obtain_auth_token,
         name='api-token-auth'),
    path('admin/', admin.site.urls),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
