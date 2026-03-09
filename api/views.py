import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, generics
from .serializers import *
from .models import *


# Filtros personalizados para filtrar por organization slug
class CategoryFilter(django_filters.FilterSet):
    org_slug = django_filters.CharFilter(field_name='organization__slug', lookup_expr='iexact')

    class Meta:
        model = Category
        fields = ['state', 'parent', 'organization', 'org_slug']


class ProductFilterByOrg(django_filters.FilterSet):
    org_slug = django_filters.CharFilter(field_name='catalogue__organization__slug', lookup_expr='iexact')
    catalogue_slug = django_filters.CharFilter(field_name='catalogue__slug', lookup_expr='iexact')
    catalogue_code = django_filters.CharFilter(field_name='catalogue__code', lookup_expr='iexact')
    id_in = django_filters.BaseInFilter(field_name='id', lookup_expr='in')

    class Meta:
        model = Product
        fields = ['state', 'brand', 'categories', 'catalogue', 'org_slug', 'catalogue_slug', 'catalogue_code', 'id_in', 'categories__name', 'categories__id', 'brand__name', 'brand__id']


class BrandFilter(django_filters.FilterSet):
    org_slug = django_filters.CharFilter(field_name='organization__slug', lookup_expr='iexact')

    class Meta:
        model = Brand
        fields = ['state', 'organization', 'org_slug']


class SlideFilter(django_filters.FilterSet):
    org_slug = django_filters.CharFilter(field_name='catalogue__organization__slug', lookup_expr='iexact')
    catalogue_slug = django_filters.CharFilter(field_name='catalogue__slug', lookup_expr='iexact')
    catalogue_code = django_filters.CharFilter(field_name='catalogue__code', lookup_expr='iexact')

    class Meta:
        model = Slide
        fields = ['state', 'virtual', 'catalogue', 'org_slug', 'catalogue_slug', 'catalogue_code']

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
    filterset_class = CategoryFilter
    ordering_fields = ['order', 'name', 'created']
    ordering = ['order', 'name']


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(parent=None, virtual=False)
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['name', 'sku', 'description', 'short_description']
    filterset_class = ProductFilterByOrg
    ordering_fields = ['name', 'price_1', 'created']
    ordering = ['name']


class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.filter(parent=None)
    serializer_class = BrandSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['name', 'description']
    filterset_class = BrandFilter
    ordering_fields = ['order', 'name']
    ordering = ['order', 'name']


class SlideViewSet(viewsets.ModelViewSet):
    queryset = Slide.objects.filter(parent=None)
    serializer_class = SlideSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['name', 'description']
    filterset_class = SlideFilter
    ordering_fields = ['order', 'name', 'created']
    ordering = ['order', 'name']


class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['name', 'slug', 'description']
    ordering_fields = ['name', 'created']
    ordering = ['name']


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


class CatalogueListView(generics.ListAPIView):
    queryset = Catalogue.objects.all().select_related('organization')
    serializer_class = CatalogueListSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['name', 'code', 'slug', 'description', 'organization__name', 'organization__slug']
    ordering_fields = ['name', 'code', 'created_at', 'updated_at']
    ordering = ['name']

    def get_serializer_class(self):
        full = self.request.query_params.get('full', 'false').lower() in ['1', 't', 'true', 'y', 'yes']
        if full:
            return CompleteCatalogueSerializer
        return CatalogueListSerializer


class PlaylistViewSet(viewsets.ModelViewSet):
    queryset = Playlist.objects.filter(is_removed=False).select_related('organization')
    serializer_class = PlaylistSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['name', 'slug', 'description']
    filterset_fields = ['is_active', 'organization']
    ordering_fields = ['name', 'created', 'modified']
    ordering = ['name']


class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.filter(is_removed=False).select_related('playlist', 'organization')
    serializer_class = VideoSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['name', 'description']
    filterset_fields = ['is_active', 'orientation', 'playlist', 'organization']
    ordering_fields = ['order', 'name', 'created', 'modified']
    ordering = ['playlist', 'order', 'name']


class CompleteCatalogueView(APIView):
    """
    Vista para obtener toda la información de un catálogo por su código

    GET /api/catalogue/<code>/

    Retorna:
    - Información del catálogo
    - Información de la organización
    - Todos los productos (con imágenes, categorías, marcas)
    - Todas las categorías de la organización
    - Todas las marcas de la organización
    - Todos los slides del catálogo
    - Configuración del cliente
    """

    def get(self, request, code):
        try:
            # Buscar catálogo por code
            catalogue = Catalogue.objects.select_related('organization').filter(
                code=code,
                is_active=True
            ).first()

            if not catalogue:
                return Response(
                    {
                        'error': 'Catálogo no encontrado',
                        'code': code
                    },
                    status=status.HTTP_404_NOT_FOUND
                )

            # Serializar con toda la información
            serializer = CompleteCatalogueSerializer(catalogue, context={'request': request})

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {
                    'error': 'Error al obtener el catálogo',
                    'detail': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ClientConfigurationViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar las configuraciones de cliente
    """
    queryset = ClientConfiguration.objects.filter(is_active=True)
    serializer_class = ClientConfigurationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'domain', 'description']
    filterset_fields = ['is_active', 'catalogue']  # organization_id fue eliminado
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
