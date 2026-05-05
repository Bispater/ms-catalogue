from django.contrib import admin
from .models import Product, Category, Brand, Images, ImportFile, MetaData, Organization, Catalogue, Slide, ClientConfiguration, Playlist, Video, CataloguePlaylist, Order, OrderItem, Terminal
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


# Inline para CataloguePlaylist en Catalogue
class CataloguePlaylistInline(admin.TabularInline):
    model = CataloguePlaylist
    extra = 1
    fields = ['playlist', 'start_date', 'end_date', 'order', 'is_active']
    readonly_fields = []


@admin.register(Catalogue)
class CatalogueAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'organization', 'currency', 'is_active', 'created_at')
    list_filter = ('organization', 'currency', 'is_active', 'created_at')
    search_fields = ('code', 'name', 'description', 'slug')
    list_editable = ('is_active',)
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ClientConfigurationInline, CataloguePlaylistInline]
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


# Inline para Videos en Playlist
class VideoInline(admin.StackedInline):
    model = Video
    extra = 1
    fields = ['name', 'description', 'file', 'thumbnail', 'orientation', 'duration', 'order', 'is_active']
    readonly_fields = ['thumbnail', 'orientation', 'duration']
    classes = ['collapse']


@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization', 'duration', 'is_active', 'created']
    list_filter = ['organization', 'is_active', 'created']
    search_fields = ['name', 'description', 'slug']  # Para autocomplete
    list_editable = ['is_active']
    readonly_fields = ('created', 'modified', 'duration')
    inlines = [VideoInline]
    fieldsets = (
        ('Información Básica', {
            'fields': ('organization', 'name', 'slug', 'description', 'tags')
        }),
        ('Configuración', {
            'fields': ('is_active', 'duration', 'state')
        }),
        ('Imágenes', {
            'fields': ('image', 'images'),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('created', 'modified'),
            'classes': ('collapse',)
        })
    )
    prepopulated_fields = {'slug': ('name',)}
    
    def save_model(self, request, obj, form, change):
        """Calcular duración al guardar"""
        super().save_model(request, obj, form, change)
        obj.duration = obj.calculate_duration()
        obj.save(update_fields=['duration'])


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['name', 'playlist', 'organization', 'orientation', 'duration', 'order', 'is_active', 'created']
    list_filter = ['playlist', 'organization', 'orientation', 'is_active', 'created']
    search_fields = ['name', 'description']
    list_editable = ['order', 'is_active']
    readonly_fields = ('created', 'modified')
    fieldsets = (
        ('Información Básica', {
            'fields': ('playlist', 'organization', 'name', 'description')
        }),
        ('Archivo de Video', {
            'fields': ('file', 'thumbnail', 'orientation', 'duration')
        }),
        ('Configuración', {
            'fields': ('order', 'is_active')
        }),
        ('Fechas', {
            'fields': ('created', 'modified'),
            'classes': ('collapse',)
        })
    )


@admin.register(CataloguePlaylist)
class CataloguePlaylistAdmin(admin.ModelAdmin):
    list_display = ['catalogue', 'playlist', 'start_date', 'end_date', 'order', 'is_active', 'is_current_status']
    list_filter = ['catalogue', 'is_active', 'start_date', 'end_date']
    search_fields = ['catalogue__name', 'playlist__name']
    list_editable = ['order', 'is_active']
    readonly_fields = ('created', 'modified', 'is_current_status')
    date_hierarchy = 'start_date'
    autocomplete_fields = ['catalogue', 'playlist']
    
    fieldsets = (
        ('Asociación', {
            'fields': ('catalogue', 'playlist')
        }),
        ('Vigencia', {
            'fields': ('start_date', 'end_date', 'is_current_status')
        }),
        ('Configuración', {
            'fields': ('order', 'is_active')
        }),
        ('Fechas', {
            'fields': ('created', 'modified'),
            'classes': ('collapse',)
        })
    )
    
    def is_current_status(self, obj):
        """Muestra si la asignación está vigente actualmente"""
        if not obj.pk:
            return "-"  # Objeto nuevo, aún no guardado
        try:
            if obj.is_current():
                return "✅ Vigente"
            return "❌ No vigente"
        except:
            return "-"
    is_current_status.short_description = "Estado actual"


# ==================== Órdenes / Ventas ====================

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ['product', 'name_snapshot', 'sku_snapshot', 'quantity', 'unit_price', 'line_total']
    readonly_fields = ['name_snapshot', 'sku_snapshot', 'quantity', 'unit_price', 'line_total']
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'created', 'local_order_number', 'catalogue',
        'authorization_code', 'card_brand', 'last_4_digits',
        'total', 'currency', 'status',
    )
    list_filter = (
        'status', 'currency', 'card_type', 'card_brand',
        'catalogue', 'catalogue__organization',
        'created',
    )
    search_fields = (
        'external_transaction_id', 'authorization_code', 'local_order_number',
        'ticket', 'terminal_id', 'last_4_digits',
    )
    readonly_fields = (
        'created', 'modified', 'is_removed',
        'external_transaction_id', 'raw_response',
    )
    date_hierarchy = 'created'
    inlines = [OrderItemInline]
    fieldsets = (
        ('Identidad', {
            'fields': ('catalogue', 'external_transaction_id', 'local_order_number', 'status'),
        }),
        ('Totales', {
            'fields': ('currency', 'subtotal', 'total'),
        }),
        ('Transbank', {
            'fields': (
                'authorization_code', 'operation_number', 'terminal_id', 'commerce_code',
                'card_type', 'card_brand', 'last_4_digits',
                'accounting_date', 'real_date', 'real_time',
                'response_code', 'response_message', 'ticket',
            ),
        }),
        ('Auditoría', {
            'fields': ('raw_response', 'notes', 'created', 'modified', 'is_removed'),
            'classes': ('collapse',),
        }),
    )


# ==================== Terminales ====================

@admin.register(Terminal)
class TerminalAdmin(admin.ModelAdmin):
    list_display = (
        'code', 'catalogue', 'pos_terminal_id', 'port',
        'connected', 'last_state', 'last_heartbeat_at',
    )
    list_filter = ('connected', 'last_state', 'catalogue', 'catalogue__organization')
    search_fields = ('code', 'pos_terminal_id', 'commerce_code', 'port')
    readonly_fields = ('last_heartbeat_at', 'last_poll_at', 'created', 'modified')
    fieldsets = (
        ('Identidad', {
            'fields': ('catalogue', 'code', 'pos_terminal_id', 'commerce_code', 'service_version'),
        }),
        ('Estado', {
            'fields': ('connected', 'keys_loaded', 'port', 'last_state', 'last_state_message'),
        }),
        ('Telemetría', {
            'fields': ('last_heartbeat_at', 'last_poll_at', 'created', 'modified'),
            'classes': ('collapse',),
        }),
        ('Notas', {
            'fields': ('notes',),
            'classes': ('collapse',),
        }),
    )
