import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, generics
from rest_framework.decorators import action
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


class CataloguePlaylistFilter(django_filters.FilterSet):
    catalogue_code = django_filters.CharFilter(field_name='catalogue__code', lookup_expr='iexact')
    org_slug = django_filters.CharFilter(field_name='catalogue__organization__slug', lookup_expr='iexact')

    class Meta:
        model = CataloguePlaylist
        fields = ['catalogue', 'catalogue_code', 'playlist', 'is_active', 'org_slug']


class CataloguePlaylistViewSet(viewsets.ModelViewSet):
    """
    CRUD de asignaciones Playlist→Catalogue con vigencia (start_date, end_date).
    """
    queryset = CataloguePlaylist.objects.filter(is_removed=False).select_related(
        'catalogue', 'catalogue__organization', 'playlist'
    )
    serializer_class = CataloguePlaylistSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = CataloguePlaylistFilter
    ordering_fields = ['catalogue', 'order', 'start_date', 'created']
    ordering = ['catalogue', 'order', 'start_date']

    def create(self, request, *args, **kwargs):
        # El unique_together (catalogue, playlist, start_date) se aplica a TODA
        # la tabla, incluyendo filas soft-deleted (is_removed=True). El validador
        # de DRF no las ve (usa el manager por defecto), así que pasaba la
        # validación y la INSERT explotaba con IntegrityError → 500.
        # Si encontramos una soft-deleted con la misma tripleta, la "resucitamos".
        catalogue = request.data.get('catalogue')
        playlist = request.data.get('playlist')
        start_date = request.data.get('start_date') or None

        if catalogue and playlist:
            existing = CataloguePlaylist.all_objects.filter(
                catalogue_id=catalogue,
                playlist_id=playlist,
                start_date=start_date,
                is_removed=True,
            ).first()
            if existing:
                existing.is_removed = False
                serializer = self.get_serializer(existing, data=request.data, partial=False)
                serializer.is_valid(raise_exception=True)
                serializer.save(is_removed=False)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        return super().create(request, *args, **kwargs)


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
    ViewSet para gestionar las configuraciones de cliente.

    Lookup por id (default). Para buscar por nombre/dominio existen los
    endpoints alternos /api/client-config/<name>/ y /api/client-config-by-domain/.
    """
    queryset = ClientConfiguration.objects.filter(is_removed=False)
    serializer_class = ClientConfigurationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'domain', 'description']
    filterset_fields = ['is_active', 'catalogue']  # organization_id fue eliminado


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


# ==================== Órdenes / Ventas ====================

class OrderFilter(django_filters.FilterSet):
    org_slug = django_filters.CharFilter(field_name='catalogue__organization__slug', lookup_expr='iexact')
    catalogue_code = django_filters.CharFilter(field_name='catalogue__code', lookup_expr='iexact')
    created_from = django_filters.IsoDateTimeFilter(field_name='created', lookup_expr='gte')
    created_to = django_filters.IsoDateTimeFilter(field_name='created', lookup_expr='lte')
    min_total = django_filters.NumberFilter(field_name='total', lookup_expr='gte')
    max_total = django_filters.NumberFilter(field_name='total', lookup_expr='lte')
    status__in = django_filters.BaseInFilter(field_name='status', lookup_expr='in')

    class Meta:
        model = Order
        fields = [
            'status', 'status__in', 'catalogue', 'catalogue_code', 'org_slug',
            'card_brand', 'card_type', 'terminal_id',
            'created_from', 'created_to', 'min_total', 'max_total',
        ]


class OrderViewSet(viewsets.ModelViewSet):
    """
    CRUD de ventas. POST /api/order/ es lo que invoca el totem tras la
    aprobación del POS Transbank. Idempotente vía external_transaction_id.
    """
    queryset = (
        Order.objects.filter(is_removed=False)
        .select_related('catalogue', 'catalogue__organization')
        .prefetch_related('items')
    )
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    search_fields = [
        'external_transaction_id', 'authorization_code', 'local_order_number',
        'ticket', 'terminal_id', 'last_4_digits',
    ]
    filterset_class = OrderFilter
    ordering_fields = ['created', 'total']
    ordering = ['-created']

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer

    def create(self, request, *args, **kwargs):
        """
        Idempotencia: si ya existe una Order con el mismo external_transaction_id,
        devolvemos la existente con HTTP 200 en vez de crear una duplicada. Esto
        permite al totem reintentar el POST sin riesgo si la red se cortó.
        """
        external_id = request.data.get('external_transaction_id')
        if external_id:
            existing = Order.objects.filter(external_transaction_id=external_id).first()
            if existing:
                return Response(
                    OrderSerializer(existing).data,
                    status=status.HTTP_200_OK,
                )

        write_serializer = self.get_serializer(data=request.data)
        write_serializer.is_valid(raise_exception=True)
        order = write_serializer.save()

        # Generar local_order_number si el cliente no lo envió: secuencia diaria
        # de 4 dígitos por catálogo (suficiente para el voucher).
        if not order.local_order_number:
            from django.utils import timezone
            today = timezone.now().date()
            count_today = Order.objects.filter(
                catalogue=order.catalogue,
                created__date=today,
            ).count()
            order.local_order_number = str(count_today).zfill(4)
            order.save(update_fields=['local_order_number'])

        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED,
        )


# ==================== Terminales ====================

class TerminalFilter(django_filters.FilterSet):
    catalogue_code = django_filters.CharFilter(field_name='catalogue__code', lookup_expr='iexact')
    org_slug = django_filters.CharFilter(field_name='catalogue__organization__slug', lookup_expr='iexact')

    class Meta:
        model = Terminal
        fields = ['catalogue', 'catalogue_code', 'org_slug', 'connected', 'last_state', 'attention_required']


class TerminalViewSet(viewsets.ModelViewSet):
    """
    CRUD de terminales (totems con POS). El POST /api/terminal/heartbeat/ es la
    forma usual de aparición: el servicio del totem hace upsert ahí cada minuto.
    """
    queryset = Terminal.objects.select_related('catalogue', 'catalogue__organization').all()
    serializer_class = TerminalSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = TerminalFilter
    search_fields = ['code', 'pos_terminal_id', 'commerce_code', 'port']
    ordering_fields = ['code', 'last_heartbeat_at', 'created']
    ordering = ['catalogue', 'code']

    @action(detail=False, methods=['post'], url_path='alert')
    def raise_alert(self, request):
        """
        POST /api/terminal/alert/
        Body: { catalogue_code, code, message? }

        El totem llama acá cuando algo falla y el cliente final pide ayuda.
        Marca el Terminal con attention_required=True para que aparezca en el admin.
        """
        from django.utils import timezone

        serializer = TerminalAlertSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            catalogue = Catalogue.objects.get(code=data['catalogue_code'])
        except Catalogue.DoesNotExist:
            return Response(
                {'detail': f'No existe catálogo con código {data["catalogue_code"]}'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        terminal, _created = Terminal.objects.get_or_create(
            catalogue=catalogue,
            code=data['code'],
        )
        terminal.attention_required = True
        terminal.attention_message = data.get('message') or 'El totem solicita atención'
        terminal.attention_requested_at = timezone.now()
        # Nueva alerta → resetear acknowledged para que cuente como no leída
        terminal.attention_acknowledged_at = None
        terminal.save(update_fields=[
            'attention_required', 'attention_message',
            'attention_requested_at', 'attention_acknowledged_at', 'modified',
        ])
        return Response(TerminalSerializer(terminal).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='ack-alert')
    def ack_alert(self, request, pk=None):
        """
        POST /api/terminal/<id>/ack-alert/
        Marca la alerta como vista (paso intermedio antes de resolver).
        La alerta sigue activa pero deja de contar como "no leída" en el badge.
        """
        from django.utils import timezone
        terminal = self.get_object()
        if terminal.attention_required and not terminal.attention_acknowledged_at:
            terminal.attention_acknowledged_at = timezone.now()
            terminal.save(update_fields=['attention_acknowledged_at', 'modified'])
        return Response(TerminalSerializer(terminal).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='resolve-alert')
    def resolve_alert(self, request, pk=None):
        """
        POST /api/terminal/<id>/resolve-alert/
        Marca la alerta como resuelta. Se llama desde el admin.
        """
        terminal = self.get_object()
        terminal.attention_required = False
        terminal.attention_message = None
        terminal.attention_requested_at = None
        terminal.attention_acknowledged_at = None
        terminal.save(update_fields=[
            'attention_required', 'attention_message',
            'attention_requested_at', 'attention_acknowledged_at', 'modified',
        ])
        return Response(TerminalSerializer(terminal).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='heartbeat')
    def heartbeat(self, request):
        """
        POST /api/terminal/heartbeat/

        Upsert por (catalogue_code, code). Crea el Terminal si no existe.
        Actualiza estado, heartbeat y poll timestamps.
        """
        from django.utils import timezone

        serializer = TerminalHeartbeatSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            catalogue = Catalogue.objects.get(code=data['catalogue_code'])
        except Catalogue.DoesNotExist:
            return Response(
                {'detail': f'No existe catálogo con código {data["catalogue_code"]}'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        terminal, _created = Terminal.objects.get_or_create(
            catalogue=catalogue,
            code=data['code'],
        )

        # Aplicar campos opcionales si vinieron
        for field in ('pos_terminal_id', 'commerce_code', 'port',
                      'connected', 'keys_loaded',
                      'last_state', 'last_state_message',
                      'last_poll_at', 'service_version'):
            if field in data and data[field] is not None:
                setattr(terminal, field, data[field])

        terminal.last_heartbeat_at = timezone.now()
        terminal.save()

        return Response(TerminalSerializer(terminal).data, status=status.HTTP_200_OK)
