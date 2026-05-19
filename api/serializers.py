from rest_framework import serializers
from .models import *
from .utils import CurrencyFormatter


class CategoryLiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class CategoryBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class CategoryBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class SlideSerializer(serializers.ModelSerializer):
    class Meta:
        model = Slide
        fields = '__all__'


class ImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Images
        fields = '__all__'


class CategoryLiteSerializer(serializers.ModelSerializer):
    childs = serializers.SerializerMethodField()
    parent = CategoryBasicSerializer()

    def get_childs(self, obj):
        result = None
        try:
            queryset = Category.objects.filter(parent=obj, virtual=False)
            if queryset.exists():
                serializer = CategoryLiteSerializer(queryset, many=True)
                result = serializer.data
        except Exception as ex:
            print(ex)
        return result

    class Meta:
        model = Category
        fields = ['id', 'name', 'parent', 'childs']


class CategorySerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        self.fields['parent'] = CategoryBasicSerializer()
        self.fields['childs'] = serializers.SerializerMethodField()
        return super(CategorySerializer, self).to_representation(instance)

    def get_childs(self, obj):
        result = None
        try:
            queryset = Category.objects.filter(parent=obj, virtual=False)
            if queryset.exists():
                serializer = CategorySerializer(queryset, many=True)
                result = serializer.data
        except Exception as ex:
            print(ex)
        return result

    class Meta:
        model = Category
        fields = '__all__'


class BrandSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        self.fields['parent'] = BrandSerializer()
        return super(BrandSerializer, self).to_representation(instance)

    class Meta:
        model = Brand
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    tags_list = serializers.SerializerMethodField()

    def get_tags_list(self, obj):
        """Retorna las tags como lista"""
        return obj.get_tags_list()

    def to_representation(self, instance):
        self.fields['variations'] = serializers.SerializerMethodField()
        self.fields['brand'] = BrandSerializer()
        self.fields['images'] = ImagesSerializer(many=True)
        self.fields['categories'] = serializers.SerializerMethodField()

        # Obtener representación base
        data = super(ProductSerializer, self).to_representation(instance)

        # Formatear precios según la moneda del catálogo
        # Determinar la moneda a usar
        currency = None
        if instance.catalogue and hasattr(instance.catalogue, 'currency') and instance.catalogue.currency:
            currency = instance.catalogue.currency
        elif hasattr(instance, 'currency') and instance.currency:
            # Si el producto tiene su propia moneda
            currency = instance.currency
        else:
            # Por defecto usar CLP
            currency = 'CLP'

        # Formatear precios usando CurrencyFormatter
        if 'price_1' in data and data['price_1']:
            data['price_1_formatted'] = CurrencyFormatter.format(data['price_1'], currency)
        if 'price_2' in data and data['price_2']:
            data['price_2_formatted'] = CurrencyFormatter.format(data['price_2'], currency)

        # Agregar información de moneda
        data['currency'] = currency
        data['currency_info'] = CurrencyFormatter.get_currency_info(currency)

        return data

    def get_variations(self, obj):
        result = None
        try:
            queryset = Product.objects.filter(parent=obj)
            if queryset.exists():
                serializer = ProductSerializer(queryset, many=True)
                result = serializer.data
        except Exception as ex:
            print(ex)
        return result

    def get_categories(self, obj):
        result = None
        try:
            serializer = CategoryBaseSerializer(obj.categories, many=True)
            result = serializer.data
        except Exception as ex:
            print(ex)
        return result

    class Meta:
        model = Product
        fields = '__all__'


class ClientConfigurationSerializer(serializers.ModelSerializer):
    """
    Serializer para la configuración del cliente
    """
    logo_url = serializers.SerializerMethodField()
    favicon_url = serializers.SerializerMethodField()
    upsell_product_detail = serializers.SerializerMethodField()

    def get_logo_url(self, obj):
        """Obtiene la URL completa del logo"""
        if obj.logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.logo.url)
            return obj.logo.url
        return None

    def get_favicon_url(self, obj):
        """Obtiene la URL completa del favicon"""
        if obj.favicon:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.favicon.url)
            return obj.favicon.url
        return None

    def get_upsell_product_detail(self, obj):
        """Snapshot mínimo del producto sugerido (evita lookup extra en el totem)."""
        product = obj.upsell_product
        if not product or product.is_removed:
            return None
        request = self.context.get('request')
        image_url = None
        if product.image:
            try:
                image_url = request.build_absolute_uri(product.image.url) if request else product.image.url
            except Exception:
                image_url = None
        return {
            'id': product.id,
            'name': product.name,
            'sku': product.sku,
            'price': float(product.price_1) if product.price_1 is not None else None,
            'image': image_url,
            'short_description': product.short_description,
        }

    class Meta:
        model = ClientConfiguration
        fields = [
            'id', 'catalogue', 'name', 'primary_color',
            'secondary_color', 'accent_color', 'logo', 'favicon',
            'logo_url', 'favicon_url', 'domain', 'description',
            'metadata', 'theme_version',
            'upsell_enabled', 'upsell_product', 'upsell_product_detail',
            'upsell_title', 'upsell_description', 'upsell_price', 'upsell_cta_label',
            'is_active', 'created', 'modified'
        ]
        read_only_fields = ['created', 'modified', 'upsell_product_detail']


class OrganizationSerializer(serializers.ModelSerializer):
    """
    Serializer para Organization
    """
    class Meta:
        model = Organization
        fields = ['id', 'name', 'slug', 'description', 'created_at', 'updated_at']


class CatalogueListSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer(read_only=True)

    class Meta:
        model = Catalogue
        fields = [
            'id', 'name', 'code', 'slug', 'description',
            'is_active', 'created_at', 'updated_at', 'organization'
        ]


class VideoSerializer(serializers.ModelSerializer):
    """
    Serializer para Video
    """
    file_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()

    def get_file_url(self, obj):
        """Obtiene la URL completa del archivo de video"""
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None

    def get_thumbnail_url(self, obj):
        """Obtiene la URL completa del thumbnail"""
        if obj.thumbnail:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.thumbnail.url)
            return obj.thumbnail.url
        return None

    class Meta:
        model = Video
        fields = [
            'id', 'name', 'description', 'file', 'file_url',
            'thumbnail', 'thumbnail_url', 'orientation', 'duration',
            'order', 'is_active', 'created', 'modified'
        ]


class PlaylistSerializer(serializers.ModelSerializer):
    """
    Serializer para Playlist con sus videos
    """
    videos = serializers.SerializerMethodField()

    def get_videos(self, obj):
        """Obtiene videos activos ordenados"""
        videos = obj.videos.filter(
            is_active=True,
            is_removed=False
        ).order_by('order', 'name')
        return VideoSerializer(videos, many=True, context=self.context).data

    class Meta:
        model = Playlist
        fields = [
            'id', 'name', 'slug', 'description', 'duration',
            'is_active', 'videos', 'created', 'modified'
        ]


class CompleteCatalogueSerializer(serializers.ModelSerializer):
    """
    Serializer completo para Catalogue con todas sus relaciones
    """
    organization = OrganizationSerializer(read_only=True)
    products = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()
    brands = serializers.SerializerMethodField()
    slides = serializers.SerializerMethodField()
    client_configuration = serializers.SerializerMethodField()
    playlists = serializers.SerializerMethodField()

    def get_products(self, obj):
        """Obtiene todos los productos del catálogo (no eliminados, no variaciones)"""
        products = Product.objects.filter(
            catalogue=obj,
            is_removed=False,
            parent=None,
            virtual=False
        ).select_related('brand').prefetch_related('categories', 'images')
        return ProductSerializer(products, many=True, context=self.context).data

    def get_categories(self, obj):
        """Obtiene todas las categorías de la organización"""
        categories = Category.objects.filter(
            organization=obj.organization,
            virtual=False
        ).select_related('parent')
        return CategorySerializer(categories, many=True, context=self.context).data

    def get_brands(self, obj):
        """Obtiene todas las marcas de la organización"""
        brands = Brand.objects.filter(
            organization=obj.organization,
            virtual=False
        ).select_related('parent')
        return BrandSerializer(brands, many=True, context=self.context).data

    def get_slides(self, obj):
        """Obtiene todos los slides del catálogo"""
        slides = Slide.objects.filter(
            catalogue=obj,
            virtual=False,
            state='publish'
        )
        return SlideSerializer(slides, many=True, context=self.context).data

    def get_client_configuration(self, obj):
        """Obtiene la configuración del cliente para este catálogo"""
        try:
            # Buscar configuración específica del catálogo (no eliminada)
            config = ClientConfiguration.objects.filter(
                catalogue=obj,
                is_active=True,
                is_removed=False
            ).first()

            if config:
                return ClientConfigurationSerializer(config, context=self.context).data
        except Exception as e:
            import traceback
            print(f"Error obteniendo configuración: {e}")
            print(traceback.format_exc())
        return None

    def get_playlists(self, obj):
        """
        Obtiene playlists vigentes del catálogo agrupadas por orientación

        Retorna:
        {
            "vertical": [
                {
                    "id": 1,
                    "name": "Playlist Vertical 1",
                    "videos": [...]
                }
            ],
            "horizontal": [
                {
                    "id": 2,
                    "name": "Playlist Horizontal 1",
                    "videos": [...]
                }
            ]
        }
        """
        from django.utils import timezone
        from django.db.models import Q, Prefetch

        now = timezone.now()

        # Obtener CataloguePlaylist vigentes
        catalogue_playlists = CataloguePlaylist.objects.filter(
            catalogue=obj,
            is_active=True,
            is_removed=False
        ).filter(
            # Sin start_date O start_date <= now
            Q(start_date__isnull=True) | Q(start_date__lte=now)
        ).filter(
            # Sin end_date O end_date > now
            Q(end_date__isnull=True) | Q(end_date__gt=now)
        ).select_related('playlist').prefetch_related(
            Prefetch(
                'playlist__videos',
                queryset=Video.objects.filter(
                    is_active=True,
                    is_removed=False
                ).order_by('order', 'name')
            )
        ).order_by('order', 'start_date')

        # Agrupar por orientación
        result = {
            'vertical': [],
            'horizontal': []
        }

        for cp in catalogue_playlists:
            playlist = cp.playlist
            if not playlist or not playlist.is_active:
                continue

            # Obtener videos activos
            videos = playlist.videos.filter(
                is_active=True,
                is_removed=False
            ).order_by('order', 'name')

            if not videos.exists():
                continue

            # Agrupar videos por orientación
            vertical_videos = []
            horizontal_videos = []

            for video in videos:
                video_data = VideoSerializer(video, context=self.context).data
                if video.orientation == 'vertical':
                    vertical_videos.append(video_data)
                else:
                    horizontal_videos.append(video_data)

            # Agregar playlist a la categoría correspondiente si tiene videos
            if vertical_videos:
                result['vertical'].append({
                    'id': playlist.id,
                    'name': playlist.name,
                    'slug': playlist.slug,
                    'description': playlist.description,
                    'duration': playlist.duration,
                    'order': cp.order,
                    'videos': vertical_videos
                })

            if horizontal_videos:
                result['horizontal'].append({
                    'id': playlist.id,
                    'name': playlist.name,
                    'slug': playlist.slug,
                    'description': playlist.description,
                    'duration': playlist.duration,
                    'order': cp.order,
                    'videos': horizontal_videos
                })

        return result

    class Meta:
        model = Catalogue
        fields = [
            'id', 'name', 'code', 'slug', 'description', 'is_active',
            'created_at', 'updated_at', 'organization', 'products',
            'categories', 'brands', 'slides', 'client_configuration', 'playlists'
        ]


# ==================== Órdenes / Ventas ====================

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'name_snapshot', 'sku_snapshot',
            'quantity', 'unit_price', 'line_total'
        ]


class OrderItemWriteSerializer(serializers.Serializer):
    """Item recibido desde el totem al crear la orden."""
    product_id = serializers.IntegerField(required=False, allow_null=True)
    name = serializers.CharField(max_length=250)
    sku = serializers.CharField(max_length=250, required=False, allow_blank=True, allow_null=True)
    quantity = serializers.IntegerField(min_value=1)
    unit_price = serializers.DecimalField(max_digits=12, decimal_places=2)


class OrderSerializer(serializers.ModelSerializer):
    """Lectura de Order — incluye items embebidos y un cache liviano del catálogo."""
    items = OrderItemSerializer(many=True, read_only=True)
    catalogue_code = serializers.CharField(source='catalogue.code', read_only=True)
    catalogue_name = serializers.CharField(source='catalogue.name', read_only=True)
    organization_name = serializers.CharField(source='catalogue.organization.name', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'catalogue', 'catalogue_code', 'catalogue_name', 'organization_name',
            'external_transaction_id', 'local_order_number', 'status',
            'currency', 'subtotal', 'total',
            'authorization_code', 'operation_number', 'terminal_id', 'commerce_code',
            'card_type', 'card_brand', 'last_4_digits',
            'accounting_date', 'real_date', 'real_time',
            'response_code', 'response_message', 'ticket',
            'raw_response', 'notes',
            'items',
            'created', 'modified', 'is_removed',
        ]
        read_only_fields = ['created', 'modified', 'is_removed']


class OrderCreateSerializer(serializers.ModelSerializer):
    """
    Serializer de escritura usado por el totem.
    Acepta `catalogue_code` para resolver el catálogo por código (más cómodo
    que pasar el ID) e `items[]` con snapshot de productos.
    """
    catalogue_code = serializers.CharField(write_only=True, required=False)
    items = OrderItemWriteSerializer(many=True, write_only=True)

    class Meta:
        model = Order
        fields = [
            'catalogue', 'catalogue_code',
            'external_transaction_id', 'local_order_number', 'status',
            'currency', 'subtotal', 'total',
            'authorization_code', 'operation_number', 'terminal_id', 'commerce_code',
            'card_type', 'card_brand', 'last_4_digits',
            'accounting_date', 'real_date', 'real_time',
            'response_code', 'response_message', 'ticket',
            'raw_response', 'notes',
            'items',
        ]
        extra_kwargs = {
            'catalogue': {'required': False, 'allow_null': True},
            'status': {'required': False},
        }

    def validate(self, attrs):
        # Resolver catalogue desde catalogue_code si llega
        catalogue = attrs.get('catalogue')
        catalogue_code = attrs.pop('catalogue_code', None)
        if not catalogue and catalogue_code:
            try:
                attrs['catalogue'] = Catalogue.objects.get(code=catalogue_code)
            except Catalogue.DoesNotExist:
                raise serializers.ValidationError({
                    'catalogue_code': f'No existe catálogo con código {catalogue_code}'
                })
        if not attrs.get('catalogue'):
            raise serializers.ValidationError({
                'catalogue': 'Debe enviar catalogue (id) o catalogue_code.'
            })
        return attrs

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        # local_order_number lo genera la View para evitar colisiones, pero si
        # el cliente lo envía, lo respetamos.
        order = Order.objects.create(**validated_data)
        for item in items_data:
            product = None
            product_id = item.get('product_id')
            if product_id:
                product = Product.objects.filter(pk=product_id).first()
            unit_price = item['unit_price']
            quantity = item['quantity']
            OrderItem.objects.create(
                order=order,
                product=product,
                name_snapshot=item['name'],
                sku_snapshot=item.get('sku') or (product.sku if product else None),
                quantity=quantity,
                unit_price=unit_price,
                line_total=unit_price * quantity,
            )
        return order


# ==================== Terminales ====================

class TerminalSerializer(serializers.ModelSerializer):
    catalogue_code = serializers.CharField(source='catalogue.code', read_only=True)
    catalogue_name = serializers.CharField(source='catalogue.name', read_only=True)
    is_online = serializers.BooleanField(read_only=True)

    class Meta:
        model = Terminal
        fields = [
            'id', 'catalogue', 'catalogue_code', 'catalogue_name',
            'code', 'pos_terminal_id', 'commerce_code', 'port',
            'connected', 'keys_loaded', 'last_state', 'last_state_message',
            'last_heartbeat_at', 'last_poll_at',
            'service_version', 'notes',
            'is_online',
            'created', 'modified',
        ]
        read_only_fields = ['created', 'modified', 'is_online']


class TerminalHeartbeatSerializer(serializers.Serializer):
    """Payload que envía transbank-pos-service cada N segundos."""
    catalogue_code = serializers.CharField(max_length=50)
    code = serializers.CharField(max_length=60)
    pos_terminal_id = serializers.CharField(max_length=40, required=False, allow_null=True, allow_blank=True)
    commerce_code = serializers.CharField(max_length=40, required=False, allow_null=True, allow_blank=True)
    port = serializers.CharField(max_length=40, required=False, allow_null=True, allow_blank=True)
    connected = serializers.BooleanField(required=False, default=False)
    keys_loaded = serializers.BooleanField(required=False, default=False)
    last_state = serializers.CharField(max_length=30, required=False)
    last_state_message = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    last_poll_at = serializers.DateTimeField(required=False, allow_null=True)
    service_version = serializers.CharField(max_length=40, required=False, allow_blank=True, allow_null=True)
