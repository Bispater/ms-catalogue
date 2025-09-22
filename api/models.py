from django.core.validators import FileExtensionValidator
from django.db import models
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from model_utils.models import TimeStampedModel, SoftDeletableModel
from slugify import slugify
import os


# Funciones para paths dinámicos por organización
def get_organization_image_path(instance, filename):
    """Genera path: {org_slug}/images/{filename} (GS_LOCATION ya incluye ms_catalogue)"""
    org_slug = getattr(instance.organization, 'slug', 'default') if hasattr(instance, 'organization') and instance.organization else 'default'
    return os.path.join(org_slug, 'images', filename)

def get_organization_icon_path(instance, filename):
    """Genera path: {org_slug}/icons/{filename} (GS_LOCATION ya incluye ms_catalogue)"""
    org_slug = getattr(instance.organization, 'slug', 'default') if hasattr(instance, 'organization') and instance.organization else 'default'
    return os.path.join(org_slug, 'icons', filename)

# Constantes
STOCK_STATUS = (
    ('instock', _('instock')),
    ('outofstock', _('outofstock')),
    ('onbackorder', _('onbackorder')),
)

OBJECT_STATUS = (
    ('publish', _('publish')),
    ('pending', _('pending')),
    ('private', _('private')),
    ('draft', _('draft')),
)

CURRENCY = (
    ('CLP', 'Peso Chileno (CLP)'),
    ('PEN', 'Sol (PEN)'),
)

# Modelo base para la organización
class OrganizationRelatedModel(models.Model):
    organization = models.ForeignKey(
        'Organization',
        on_delete=models.CASCADE,
        verbose_name=_('organization'),
        null=True,
        blank=True
    )

    class Meta:
        abstract = True

# Modelo para metadatos
class MetaModel(models.Model):
    meta_title = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('meta title'))
    meta_description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('meta description'))
    meta_keywords = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('meta keywords'))

    class Meta:
        abstract = True

# Decorador para prevenir recursión
class prevent_recursion(object):
    def __init__(self, func):
        self.func = func
        self.started = False

    def __call__(self, *args, **kwargs):
        if self.started:
            return None
        self.started = True
        try:
            return self.func(*args, **kwargs)
        finally:
            self.started = False

# Modelo de Imágenes
class Images(TimeStampedModel, SoftDeletableModel, OrganizationRelatedModel):
    name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('name'))
    alt = models.CharField(
        blank=True,
        null=True,
        max_length=255,
        verbose_name=_('alt'))
    code = models.CharField(
        blank=True,
        null=True,
        max_length=100,
        verbose_name=_('code'))
    image = models.ImageField(
        upload_to=get_organization_image_path,
        verbose_name=_('image')
    )

    class Meta:
        verbose_name = _('image')
        verbose_name_plural = _('images')

    def __str__(self):
        return "{}".format(self.name or self.id)

# Modelo base para categorías, marcas, etc.
class BaseModel(models.Model):
    name = models.CharField(
        max_length=250,
        verbose_name=_('name'))
    slug = models.SlugField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('slug'))
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('description'))
    image = models.ImageField(
        upload_to=get_organization_image_path,
        blank=True,
        null=True,
        verbose_name=_('image')
    )
    images = models.ManyToManyField(
        Images,
        blank=True,
        verbose_name=_('images'),
    )
    style = models.CharField(
        max_length=255,
        default='',
        blank=True,
        verbose_name=_('style'))
    state = models.CharField(
        max_length=255,
        choices=OBJECT_STATUS,
        default='publish',
        verbose_name=_('state'))

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

# Modelo de Categoría
class Category(BaseModel, OrganizationRelatedModel):
    parent = models.ForeignKey(
        'self',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='children',
        verbose_name=_('parent')
    )
    icon_file = models.ImageField(
        upload_to=get_organization_icon_path,
        blank=True,
        null=True,
        verbose_name=_('icon file')
    )
    order = models.IntegerField(
        default=0,
        blank=True,
        null=True,
        verbose_name=_('order'))
    virtual = models.BooleanField(
        default=False,
        verbose_name=_('virtual'))

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')

    def __str__(self):
        return self.name

# Modelo de Marca
class Brand(BaseModel, OrganizationRelatedModel):
    parent = models.ForeignKey(
        'self',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='children',
        verbose_name=_('parent')
    )
    order = models.IntegerField(
        default=0,
        blank=True,
        null=True,
        verbose_name=_('order'))
    virtual = models.BooleanField(
        default=False,
        verbose_name=_('virtual'))

    class Meta:
        verbose_name = _('brand')
        verbose_name_plural = _('brands')

    def __str__(self):
        return self.name

# Modelo de Dimensiones
class Dimensions(models.Model):
    length = models.DecimalField(
        default=0,
        blank=True,
        null=True,
        max_digits=12,
        decimal_places=1,
        verbose_name=_('length')
    )
    width = models.DecimalField(
        default=0,
        blank=True,
        null=True,
        max_digits=12,
        decimal_places=1,
        verbose_name=_('width')
    )
    height = models.DecimalField(
        default=0,
        blank=True,
        null=True,
        max_digits=12,
        decimal_places=1,
        verbose_name=_('height')
    )

    class Meta:
        abstract = True

# Modelo de Producto
class Product(BaseModel, TimeStampedModel, SoftDeletableModel, Dimensions, OrganizationRelatedModel):
    sku = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        unique=True,
        verbose_name=_('sku'))
    short_description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('short description'))
    currency = models.CharField(
        max_length=10,
        choices=CURRENCY,
        blank=True,
        null=True,
        verbose_name=_('currency'))
    price_1 = models.DecimalField(
        blank=True,
        null=True,
        max_digits=12,
        decimal_places=2,
        verbose_name=_('price 1')
    )
    price_2 = models.DecimalField(
        blank=True,
        null=True,
        max_digits=12,
        decimal_places=2,
        verbose_name=_('price 2')
    )
    weight = models.DecimalField(
        blank=True,
        null=True,
        max_digits=12,
        decimal_places=1,
        verbose_name=_('weight')
    )
    manage_stock = models.BooleanField(
        default=False,
        verbose_name=_('manage stock'))
    stock_quantity = models.IntegerField(
        default=0,
        blank=True,
        null=True,
        verbose_name=_('stock quantity'))
    stock_status = models.CharField(
        max_length=20,
        choices=STOCK_STATUS,
        default='instock',
        verbose_name=_('stock status'))
    parent = models.ForeignKey(
        'self',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='variations',
        verbose_name=_('parent')
    )
    brand = models.ForeignKey(
        Brand,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='products',
        verbose_name=_('brand')
    )
    categories = models.ManyToManyField(
        Category,
        blank=True,
        related_name='products',
        verbose_name=_('categories')
    )
    virtual = models.BooleanField(
        default=False,
        verbose_name=_('virtual'))

    class Meta:
        verbose_name = _('product')
        verbose_name_plural = _('products')
        ordering = ['-created']

    def __str__(self):
        variations = f" ({_('variation')})" if self.parent else ''
        return f"{self.name}{variations}"

    @property
    def is_variation(self):
        return self.parent is not None

# Modelo de Metadatos
class MetaData(MetaModel):
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name='metadata',
        verbose_name=_('product')
    )

    class Meta:
        verbose_name = _('meta data')
        verbose_name_plural = _('meta data')

    def __str__(self):
        return f"Metadata for {self.product.name}"

# Modelo para importación de archivos
class ImportFile(TimeStampedModel, SoftDeletableModel, OrganizationRelatedModel):
    file = models.FileField(
        upload_to='imports/',
        verbose_name=_('file'))
    images_zip = models.FileField(
        upload_to='imports/zips/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['zip'])],
        verbose_name=_('images zip'))
    currency = models.CharField(
        max_length=10,
        choices=CURRENCY,
        blank=True,
        null=True,
        verbose_name=_('currency'))
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('description'),
    )
    uploaded = models.BooleanField(
        default=False,
        verbose_name=_('uploaded')
    )
    remove_all = models.BooleanField(
        default=False,
        verbose_name=_('remove all')
    )
    user_created = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='imported_files',
        verbose_name=_('user created')
    )

    class Meta:
        verbose_name = _('import file')
        verbose_name_plural = _('import files')
        ordering = ['-created']

    def __str__(self):
        return self.description or f"Import File {self.id}"

# Modelo de Organización
class Organization(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name=_('name'))
    slug = models.SlugField(
        unique=True,
        verbose_name=_('slug'))
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('description'))
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('created at'))
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('updated at'))

    class Meta:
        verbose_name = _('organization')
        verbose_name_plural = _('organizations')
        ordering = ['name']

    def __str__(self):
        return self.name

    # def save(self, *args, **kwargs):
    #     if not self.slug:
    #         self.slug = slugify(self.name)
    #     super().save(*args, **kwargs)

# Modelo Slide
class Slide(BaseModel, OrganizationRelatedModel):
    parent = models.ForeignKey(
        'self',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_('parent')
    )
    order = models.IntegerField(
        default=0,
        blank=True,
        null=True,
        verbose_name=_('order'))
    virtual = models.BooleanField(
        default=False,
        verbose_name=_('virtual'))

    class Meta:
        verbose_name = _('slide')
        verbose_name_plural = _('slides')

    def __str__(self):
        return "{}".format(self.name)

# Señales
@receiver(post_save, sender=Category)
@prevent_recursion
def save_category(sender, instance=None, created=False, **kwargs):
    """
    Guarda la categoría asegurando que tenga un slug
    """
    if not instance.slug:
        instance.slug = slugify(instance.name)
        instance.save(update_fields=['slug'])

@receiver(post_save, sender=ImportFile)
@prevent_recursion
def handle_import_file(sender, instance=None, created=False, **kwargs):
    """
    Maneja la importación de archivos
    """
    if created and not instance.uploaded:
        # Aquí iría la lógica para procesar el archivo de importación
        # Por ahora, solo marcamos como subido
        instance.uploaded = True
        instance.save(update_fields=['uploaded'])
        # En producción, aquí podrías llamar a una tarea Celery
        # from .tasks import process_import_file
        # process_import_file.delay(instance.id)
