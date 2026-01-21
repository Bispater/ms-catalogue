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

    class Meta:
        model = ClientConfiguration
        fields = [
            'id', 'name', 'organization_id', 'primary_color', 
            'secondary_color', 'accent_color', 'logo', 'favicon',
            'logo_url', 'favicon_url', 'domain', 'description', 
            'is_active', 'created', 'modified'
        ]
        read_only_fields = ['created', 'modified']


class OrganizationSerializer(serializers.ModelSerializer):
    """
    Serializer para Organization
    """
    class Meta:
        model = Organization
        fields = ['id', 'name', 'slug', 'description', 'created_at', 'updated_at']


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
    
    class Meta:
        model = Catalogue
        fields = [
            'id', 'name', 'code', 'slug', 'description', 'is_active',
            'created_at', 'updated_at', 'organization', 'products',
            'categories', 'brands', 'slides', 'client_configuration'
        ]
