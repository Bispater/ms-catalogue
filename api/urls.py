from django.urls import path, include, re_path
from rest_framework import routers
from . import views

# Configuración del router
router = routers.DefaultRouter()
router.register(r'category', views.CategoryViewSet, basename='category')
router.register(r'product_view', views.ProductViewSet, basename='product')
router.register(r'brand', views.BrandViewSet, basename='brand')
router.register(r'slide', views.SlideViewSet, basename='slide')
router.register(r'client-configurations', views.ClientConfigurationViewSet, basename='client-configuration')

# URLs personalizadas
urlpatterns = [
    # Incluir las URLs del router
    re_path(r'^', include(router.urls)),
    
    # Otras URLs personalizadas
    path('product/', views.ProductView.as_view(), name='product'),
    
    # URLs para configuración de cliente
    path('client-config/<str:client_name>/', views.ClientConfigurationByNameView.as_view(), name='client-config-by-name'),
    path('client-config-by-domain/<str:domain>/', views.ClientConfigurationByDomainView.as_view(), name='client-config-by-domain'),
    
    # Ruta de ejemplo protegida por JWT
    path('example/', views.ExampleView.as_view(), name='example'),
]
