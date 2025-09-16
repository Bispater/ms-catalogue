from rest_framework import serializers
from .models import *


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
    def to_representation(self, instance):
        self.fields['variations'] = serializers.SerializerMethodField()
        self.fields['brand'] = BrandSerializer()
        self.fields['images'] = ImagesSerializer(many=True)
        self.fields['categories'] = serializers.SerializerMethodField()
        return super(ProductSerializer, self).to_representation(instance)

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
