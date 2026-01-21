from django.contrib import admin
from .models import Product, Category, Brand, Images, ImportFile, MetaData, Organization, Catalogue, Slide, ClientConfiguration
from .forms import ProductAdminForm, MyModelForm, ClientConfigurationForm

class MetaDataInline(admin.StackedInline):
    model = MetaData
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_filter = ['catalogue', 'catalogue__organization', 'currency', 'categories']
    search_fields = ['name', 'description', 'sku', 'tags']
    list_display = ['name', 'catalogue', 'brand', 'currency', 'tags', 'state']
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
    list_filter = ['catalogue', 'catalogue__organization', 'currency', 'uploaded', 'import_mode', 'user_created']
    search_fields = ['description']
    list_display = ['id', 'catalogue', 'currency', 'import_mode', 'user_created', 'created', 'description', 'file', 'uploaded', 'import_status']
    readonly_fields = ('created', 'modified', 'uploaded', 'user_created')
    exclude = ()  # No excluir nada, pero user_created será readonly
    
    def import_status(self, obj):
        """Muestra el estado de la importación"""
        if obj.uploaded:
            return "✅ Procesado Automáticamente"
        return "⏳ Procesando..."
    import_status.short_description = "Estado"
    
    def get_readonly_fields(self, request, obj=None):
        """Hacer user_created readonly siempre"""
        if obj:  # Editando
            return self.readonly_fields
        else:  # Creando nuevo
            return ('created', 'modified', 'uploaded')
    
    def get_form(self, request, obj=None, **kwargs):
        """Pre-seleccionar usuario actual al crear nuevo"""
        form = super().get_form(request, obj, **kwargs)
        if not obj and 'user_created' in form.base_fields:
            # Pre-seleccionar usuario actual
            form.base_fields['user_created'].initial = request.user.id
        return form
    
    def save_model(self, request, obj, form, change):
        """Guardar y asignar usuario automáticamente"""
        if not change:  # Si es nuevo
            obj.user_created = request.user
        super().save_model(request, obj, form, change)

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

class ClientConfigurationInline(admin.StackedInline):
    model = ClientConfiguration
    form = ClientConfigurationForm
    extra = 0
    classes = ['collapse']
    fieldsets = (
        ('Configuración del Cliente', {
            'fields': ('name', 'domain', 'description', 'is_active')
        }),
        ('Colores y Branding', {
            'fields': ('primary_color', 'secondary_color', 'accent_color', 'logo', 'favicon'),
        }),
        ('Metadata', {
            'fields': ('metadata',),
        }),
    )


@admin.register(Catalogue)
class CatalogueAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'organization', 'currency', 'is_active', 'created_at')
    list_filter = ('organization', 'currency', 'is_active', 'created_at')
    search_fields = ('code', 'name', 'description', 'slug')
    list_editable = ('is_active',)
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ClientConfigurationInline]
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'code', 'slug', 'organization', 'description', 'currency', 'is_active')
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(Slide)
class SlideAdmin(admin.ModelAdmin):
    list_filter = ['catalogue', 'catalogue__organization', 'state', 'virtual']
    search_fields = ['name', 'description']
    list_display = ['id', 'catalogue', 'name', 'order', 'parent', 'state', 'virtual']
    list_editable = ['order', 'state']
    readonly_fields = ('created_at', 'updated_at') if hasattr(Slide, 'created_at') and hasattr(Slide, 'updated_at') else ()
    ordering = ('order', 'name')


@admin.register(ClientConfiguration)
class ClientConfigurationAdmin(admin.ModelAdmin):
    form = ClientConfigurationForm
    list_display = ['name', 'catalogue', 'domain', 'primary_color', 'is_active', 'created', 'modified']
    list_filter = ['catalogue', 'catalogue__organization', 'is_active', 'created', 'modified']
    search_fields = ['name', 'domain', 'description']
    list_editable = ['is_active']
    readonly_fields = ['created', 'modified']
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'catalogue', 'domain', 'description', 'is_active')
        }),
        ('Colores y Branding', {
            'fields': ('primary_color', 'secondary_color', 'accent_color', 'logo', 'favicon'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('created', 'modified'),
            'classes': ('collapse',)
        })
    )
