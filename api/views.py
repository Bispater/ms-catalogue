import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, generics
from .serializers import *
from .models import *

# Vista de ejemplo protegida por JWT
class ExampleView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, format=None):
        content = {
            'status': 'request was permitted',
            'user': str(request.user),
            'auth': str(request.auth),
        }
        return Response(content)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.filter(virtual=False)
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['name', 'description', 'style', 'state']
    filterset_fields = ['state', 'parent']
    ordering_fields = ['order', 'name', 'created']
    ordering = ['order', 'name']


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(parent=None, virtual=False)
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['name', 'sku', 'description', 'short_description']
    filterset_fields = ['state', 'brand', 'categories']
    ordering_fields = ['name', 'price_1', 'created']
    ordering = ['name']


class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.filter(parent=None)
    serializer_class = BrandSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['name', 'description']
    filterset_fields = ['state']
    ordering_fields = ['order', 'name']
    ordering = ['order', 'name']


class SlideViewSet(viewsets.ModelViewSet):
    queryset = Slide.objects.filter(parent=None)
    serializer_class = SlideSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['name', 'description']
    filterset_fields = ['state', 'virtual', 'organization']
    ordering_fields = ['order', 'name', 'created']
    ordering = ['order', 'name']


class NumberInFilter(django_filters.BaseInFilter, django_filters.NumberFilter):
    pass


class ProductFilter(django_filters.FilterSet):
    id_in = NumberInFilter(field_name='id', lookup_expr='in')

    class Meta:
        model = Product
        fields = ['id_in', 'categories__name', 'categories__id', 'brand__name', 'brand__id']


class ProductView(generics.ListAPIView):
    queryset = Product.objects.filter(parent=None, virtual=False)
    serializer_class = ProductSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, django_filters.rest_framework.DjangoFilterBackend)
    search_fields = ('name', 'sku', 'slug', 'description', 'id', 'categories__name', 'brand__name')
    filter_class = ProductFilter


class ClientConfigurationViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar las configuraciones de cliente
    """
    queryset = ClientConfiguration.objects.filter(is_active=True)
    serializer_class = ClientConfigurationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'domain', 'description']
    filterset_fields = ['is_active', 'organization_id']
    lookup_field = 'name'  # Permite buscar por nombre en lugar de ID


class ClientConfigurationByNameView(generics.RetrieveAPIView):
    """
    Vista para obtener configuración de cliente por nombre
    Endpoint: /api/client-config/{client_name}/
    """
    queryset = ClientConfiguration.objects.filter(is_active=True)
    serializer_class = ClientConfigurationSerializer
    lookup_field = 'name'
    lookup_url_kwarg = 'client_name'

    def get_object(self):
        """
        Busca la configuración por nombre (case-insensitive)
        """
        client_name = self.kwargs.get('client_name')
        try:
            return ClientConfiguration.objects.get(
                name__iexact=client_name, 
                is_active=True
            )
        except ClientConfiguration.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound(f"No se encontró configuración para el cliente '{client_name}'")


class ClientConfigurationByDomainView(generics.RetrieveAPIView):
    """
    Vista para obtener configuración de cliente por dominio
    Endpoint: /api/client-config-by-domain/{domain}/
    """
    queryset = ClientConfiguration.objects.filter(is_active=True)
    serializer_class = ClientConfigurationSerializer
    lookup_field = 'domain'
    lookup_url_kwarg = 'domain'

    def get_object(self):
        """
        Busca la configuración por dominio
        """
        domain = self.kwargs.get('domain')
        try:
            return ClientConfiguration.objects.get(
                domain__iexact=domain, 
                is_active=True
            )
        except ClientConfiguration.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound(f"No se encontró configuración para el dominio '{domain}'")
