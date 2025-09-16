from django.contrib import admin
from .models import Product, Category, Brand, Images, ImportFile, MetaData, Organization, Slide
from .forms import ProductAdminForm, MyModelForm

class MetaDataInline(admin.StackedInline):
    model = MetaData
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_filter = ['currency', 'categories']
    search_fields = ['name', 'description', 'sku']
    list_display = ['name', 'brand', 'currency', 'short_description', 'slug', 'parent', 'state']
    inlines = [MetaDataInline]
    form = ProductAdminForm
    readonly_fields = ('created', 'modified')
    filter_horizontal = ('categories', 'images')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_filter = ['name']
    search_fields = ['name']
    list_display = ['name', 'slug', 'parent', 'style', 'state']
    form = MyModelForm
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_filter = ['name']
    search_fields = ['name']
    list_display = ['name', 'slug', 'parent', 'state']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Images)
class ImagesAdmin(admin.ModelAdmin):
    list_filter = ['code']
    search_fields = ['name', 'image']
    list_display = ['name', 'code', 'image']
    readonly_fields = ('created', 'modified')

@admin.register(ImportFile)
class ImportFileAdmin(admin.ModelAdmin):
    list_filter = ['uploaded']
    search_fields = ['description']
    list_display = ['id', 'created', 'modified', 'description', 'file', 'uploaded']
    readonly_fields = ('created', 'modified')

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}



@admin.register(Slide)
class SlideAdmin(admin.ModelAdmin):
    list_filter = ['state', 'virtual']
    search_fields = ['name', 'description']
    list_display = ['id', 'name', 'order', 'parent', 'state', 'virtual']
    list_editable = ['order', 'state']
    readonly_fields = ('created_at', 'updated_at') if hasattr(Slide, 'created_at') and hasattr(Slide, 'updated_at') else ()
    ordering = ('order', 'name')
