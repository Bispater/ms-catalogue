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
import re


# Función para generar tags automáticamente
def generate_tags_from_text(text, category_name=None):
    """
    Genera tags desde un texto, removiendo conectores y palabras comunes
    
    Args:
        text: Texto a procesar (ej: nombre del producto)
        category_name: Nombre de la categoría (opcional)
    
    Returns:
        String con tags separadas por comas
    
    Example:
        >>> generate_tags_from_text("Fernet con Cola", "Destilado")
        "fernet, cola, destilado"
    """
    if not text:
        return ""
    
    # Convertir a minúsculas
    text = text.lower()
    
    # Conectores y palabras comunes a remover (español)
    stop_words = {
        'con', 'sin', 'de', 'del', 'la', 'el', 'los', 'las', 'un', 'una', 'unos', 'unas',
        'y', 'o', 'pero', 'para', 'por', 'en', 'a', 'al', 'sobre', 'bajo', 'entre',
        'desde', 'hasta', 'hacia', 'según', 'durante', 'mediante', 'contra', 'ante'
    }
    
    # Remover caracteres especiales y dividir en palabras
    words = re.findall(r'\b[a-záéíóúñü]+\b', text)
    
    # Filtrar palabras: remover stop words y palabras muy cortas
    tags = [word for word in words if word not in stop_words and len(word) > 2]
    
    # Agregar categoría si existe
    if category_name:
        category_tags = re.findall(r'\b[a-záéíóúñü]+\b', category_name.lower())
        tags.extend([tag for tag in category_tags if tag not in stop_words and len(tag) > 2])
    
    # Remover duplicados manteniendo orden
    seen = set()
    unique_tags = []
    for tag in tags:
        if tag not in seen:
            seen.add(tag)
            unique_tags.append(tag)
    
    return ', '.join(unique_tags)


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
    ('USD', 'Dólar Estadounidense (USD)'),
    ('EUR', 'Euro (EUR)'),
    ('ARS', 'Peso Argentino (ARS)'),
    ('BRL', 'Real Brasileño (BRL)'),
    ('MXN', 'Peso Mexicano (MXN)'),
    ('COP', 'Peso Colombiano (COP)'),
    ('PEN', 'Sol Peruano (PEN)'),
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
    tags = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_('tags'),
        help_text=_('Etiquetas separadas por comas (ej: bebida, vino, líquidos)')
    )
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
        # Limpiar tags: remover espacios extras
        if self.tags:
            tags_list = [tag.strip() for tag in self.tags.split(',') if tag.strip()]
            self.tags = ', '.join(tags_list)
        super().save(*args, **kwargs)
    
    def get_tags_list(self):
        """Retorna las tags como lista"""
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
    
    def add_tag(self, tag):
        """Agrega una tag si no existe"""
        tags_list = self.get_tags_list()
        tag = tag.strip()
        if tag and tag not in tags_list:
            tags_list.append(tag)
            self.tags = ', '.join(tags_list)
            self.save(update_fields=['tags'])
    
    def remove_tag(self, tag):
        """Remueve una tag si existe"""
        tags_list = self.get_tags_list()
        tag = tag.strip()
        if tag in tags_list:
            tags_list.remove(tag)
            self.tags = ', '.join(tags_list) if tags_list else None
            self.save(update_fields=['tags'])

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
class Product(BaseModel, TimeStampedModel, SoftDeletableModel, Dimensions):
    catalogue = models.ForeignKey(
        'Catalogue',
        on_delete=models.CASCADE,
        related_name='products',
        null=True,  # Temporal para migración
        blank=True,
        verbose_name=_('catalogue'))
    sku = models.CharField(
        max_length=250,
        blank=True,
        null=True,
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
        unique_together = [['sku', 'catalogue']]

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
class ImportFile(TimeStampedModel, SoftDeletableModel):
    catalogue = models.ForeignKey(
        'Catalogue',
        on_delete=models.CASCADE,
        related_name='import_files',
        null=True,  # Temporal para migración
        blank=True,
        verbose_name=_('catalogue'))
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
        default='CLP',
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
    import_mode = models.CharField(
        max_length=20,
        choices=[
            ('update', 'Actualizar existentes y crear nuevos'),
            ('create_only', 'Solo crear nuevos (no actualizar)'),
            ('replace_all', 'Reemplazar todo (eliminar y recrear)'),
            ('soft_delete', 'Sincronizar (ocultar no incluidos)'),
        ],
        default='update',
        verbose_name=_('import mode'),
        help_text=_('Modo de importación: update (actualiza y crea), create_only (solo nuevos), replace_all (elimina todo), soft_delete (oculta no incluidos)')
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
    
    def save(self, *args, **kwargs):
        """
        Guardar y procesar automáticamente si es nuevo
        """
        is_new = self.pk is None
        should_process = is_new and self.file and self.catalogue and not self.uploaded
        
        # Guardar primero para tener el archivo en disco
        super().save(*args, **kwargs)
        
        # Procesar automáticamente si es nuevo
        if should_process:
            self.process_import()
    
    def process_import(self):
        """
        Procesa el archivo Excel e importa los productos
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            import pandas as pd
            from decimal import Decimal
            
            logger.info(f"🚀 Iniciando importación de {self.file.name}")
            
            # Leer Excel (compatible con storage local y remoto)
            with self.file.open('rb') as f:
                df = pd.read_excel(f)
            logger.info(f"📊 Excel leído: {len(df)} filas")
            logger.info(f"📋 Columnas encontradas: {list(df.columns)}")
            
            # Detectar columna SKU (buscar cualquier columna que contenga "SKU" o "sku")
            sku_column = None
            for col in df.columns:
                if 'sku' in str(col).lower():
                    sku_column = col
                    logger.info(f"✅ Columna SKU detectada: {col}")
                    break
            
            # Si no se encuentra, usar la primera columna
            if not sku_column:
                sku_column = df.columns[0]
                logger.warning(f"⚠️ No se encontró columna SKU, usando primera columna: {sku_column}")
            
            # Validar columnas requeridas (NOMBRE y PRECIO)
            required_columns = ['NOMBRE', 'PRECIO']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ValueError(f"Faltan columnas requeridas: {missing_columns}")
            
            # Estadísticas
            stats = {
                'created': 0,
                'updated': 0,
                'reactivated': 0,
                'errors': 0,
                'total': len(df)
            }
            
            # Aplicar modo de importación
            if self.import_mode == 'soft_delete':
                # Marcar todos como eliminados
                Product.objects.filter(catalogue=self.catalogue).update(is_removed=True)
            elif self.import_mode == 'replace_all':
                # Eliminar todos
                Product.objects.filter(catalogue=self.catalogue).delete()
            
            # Rastrear SKUs procesados en esta importación para detectar duplicados
            skus_procesados = set()
            
            # Procesar cada fila
            for index, row in df.iterrows():
                try:
                    # Usar SKU tal como viene en el Excel (quitar .0 si es número)
                    sku_raw = row[sku_column]
                    
                    # Validar que SKU no sea NaN o vacío
                    if pd.isna(sku_raw) or str(sku_raw).strip() == '' or str(sku_raw).strip().lower() == 'nan':
                        logger.warning(f"⚠️ Fila {index + 2}: SKU vacío, omitiendo")
                        stats['errors'] += 1
                        continue
                    
                    if isinstance(sku_raw, float):
                        # Si es float, convertir a int para quitar .0
                        sku = str(int(sku_raw))
                    else:
                        sku = str(sku_raw).strip()
                    
                    # Verificar si ya procesamos este SKU en esta importación
                    if sku in skus_procesados:
                        logger.warning(f"⚠️ Fila {index + 2}: SKU {sku} duplicado en el Excel, omitiendo")
                        stats['errors'] += 1
                        continue
                    
                    # Marcar como procesado
                    skus_procesados.add(sku)
                    
                    # Verificar si existe
                    producto_existente = Product.objects.filter(
                        sku=sku, 
                        catalogue=self.catalogue
                    ).first()
                    
                    # Modo create_only: Omitir si existe
                    if self.import_mode == 'create_only' and producto_existente:
                        continue
                    
                    # Preparar datos
                    price_1 = Decimal(str(row['PRECIO']))
                    price_2 = None
                    
                    # Buscar precio oferta con diferentes nombres de columna
                    precio_oferta = None
                    for col_name in ['PRECIO_OFERTA', 'PRECIO OFERTA', 'Precio Oferta', 'precio_oferta']:
                        if col_name in df.columns and pd.notna(row.get(col_name)):
                            precio_oferta = row[col_name]
                            break
                    
                    if precio_oferta:
                        price_2 = Decimal(str(precio_oferta))
                    else:
                        # Buscar descuento con diferentes nombres de columna
                        descuento_val = None
                        for col_name in ['DESCUENTO_EN_%', 'DESCUENTO EN %', 'DESCUENTO', 'Descuento', 'descuento']:
                            if col_name in df.columns and pd.notna(row.get(col_name)):
                                descuento_val = row[col_name]
                                break
                        
                        if descuento_val is not None:
                            # Manejar tanto string "20%" como número 20 o 0.20
                            if isinstance(descuento_val, str):
                                descuento_val = descuento_val.strip('%')
                            descuento = float(descuento_val)
                            # Si es mayor a 1, asumimos que es porcentaje (ej: 20 = 20%)
                            if descuento > 1:
                                descuento = descuento / 100
                            price_2 = price_1 * Decimal(str(1 - descuento))
                    
                    # Descripción - buscar con o sin tilde
                    descripcion = None
                    for col_name in ['DESCRIPCIÓN', 'DESCRIPCION', 'Descripción', 'Descripcion']:
                        if col_name in df.columns:
                            descripcion = row.get(col_name)
                            break
                    
                    if pd.notna(descripcion) and str(descripcion).strip():
                        descripcion_text = str(descripcion).strip()
                        logger.info(f"📝 Descripción encontrada para {sku}: {descripcion_text[:50]}...")
                        # Descripción corta: primeros 150 caracteres
                        short_description = descripcion_text[:150] + "..." if len(descripcion_text) > 150 else descripcion_text
                        # Descripción completa: texto completo en HTML
                        full_description = f"<p>{descripcion_text}</p>"
                    else:
                        logger.warning(f"⚠️ No se encontró descripción para {sku}, usando nombre")
                        short_description = row['NOMBRE']
                        full_description = ""
                    
                    # Stock - buscar columna STOCK con diferentes nombres
                    stock_quantity = 100  # Valor por defecto
                    manage_stock = False
                    stock_status = 'instock'
                    
                    for col_name in ['STOCK', 'Stock', 'stock', 'CANTIDAD', 'Cantidad']:
                        if col_name in df.columns and pd.notna(row.get(col_name)):
                            try:
                                stock_quantity = int(row[col_name])
                                manage_stock = True  # Si viene stock, activar gestión
                                # Determinar estado según cantidad
                                stock_status = 'instock' if stock_quantity > 0 else 'outofstock'
                                logger.info(f"📦 Stock para {sku}: {stock_quantity}")
                                break
                            except (ValueError, TypeError):
                                logger.warning(f"⚠️ Valor de stock inválido para {sku}: {row.get(col_name)}")
                    
                    # Datos del producto
                    product_data = {
                        'name': row['NOMBRE'],
                        'short_description': short_description,
                        'description': full_description,
                        'price_1': price_1,
                        'price_2': price_2,
                        'currency': self.currency or 'CLP',
                        'stock_status': stock_status,
                        'stock_quantity': stock_quantity,
                        'manage_stock': manage_stock,
                        'state': 'publish',
                        'virtual': False,
                    }
                    
                    # Si es modo soft_delete, reactivar
                    if self.import_mode == 'soft_delete':
                        product_data['is_removed'] = False
                    
                    # Crear o actualizar
                    product, created = Product.objects.update_or_create(
                        sku=sku,
                        catalogue=self.catalogue,
                        defaults=product_data
                    )
                    
                    # Procesar CATEGORÍA - buscar con variaciones
                    categoria_nombre = None
                    for col_name in ['CATEGORÍA', 'CATEGORIA', 'Categoría', 'Categoria']:
                        if col_name in df.columns:
                            categoria_nombre = row.get(col_name)
                            break
                    
                    if pd.notna(categoria_nombre) and categoria_nombre:
                        try:
                            categoria_nombre = str(categoria_nombre).strip()
                            # Crear o obtener categoría
                            from django.utils.text import slugify
                            categoria, cat_created = Category.objects.get_or_create(
                                slug=slugify(categoria_nombre),
                                organization=self.catalogue.organization,
                                defaults={
                                    'name': categoria_nombre,
                                    'state': 'publish',
                                    'virtual': False
                                }
                            )
                            if cat_created:
                                logger.info(f"📁 Categoría creada: {categoria_nombre}")
                            
                            # Asociar categoría al producto si no está ya asociada
                            if not product.categories.filter(id=categoria.id).exists():
                                product.categories.add(categoria)
                                logger.info(f"🔗 Categoría '{categoria_nombre}' asociada a {sku}")
                        except Exception as cat_error:
                            logger.warning(f"⚠️ Error procesando categoría para {sku}: {str(cat_error)}")
                    
                    # Generar tags automáticamente desde nombre y categoría
                    try:
                        auto_tags = generate_tags_from_text(
                            product.name,
                            categoria_nombre if pd.notna(categoria_nombre) else None
                        )
                        if auto_tags:
                            product.tags = auto_tags
                            product.save(update_fields=['tags'])
                            logger.info(f"🏷️ Tags generadas para {sku}: {auto_tags}")
                    except Exception as tag_error:
                        logger.warning(f"⚠️ Error generando tags para {sku}: {str(tag_error)}")
                    
                    # Procesar MARCA
                    marca_nombre = row.get('MARCA')
                    if pd.notna(marca_nombre) and marca_nombre:
                        try:
                            marca_nombre = str(marca_nombre).strip()
                            # Crear o obtener marca
                            from django.utils.text import slugify
                            marca, marca_created = Brand.objects.get_or_create(
                                slug=slugify(marca_nombre),
                                organization=self.catalogue.organization,
                                defaults={
                                    'name': marca_nombre,
                                    'state': 'publish',
                                    'virtual': False
                                }
                            )
                            if marca_created:
                                logger.info(f"🏷️ Marca creada: {marca_nombre}")
                            
                            # Asignar marca al producto
                            product.brand = marca
                            product.save(update_fields=['brand'])
                            logger.info(f"🔗 Marca '{marca_nombre}' asignada a {sku}")
                        except Exception as marca_error:
                            logger.warning(f"⚠️ Error procesando marca para {sku}: {str(marca_error)}")
                    
                    # Procesar IMAGEN (singular) - guardar en campo image del producto
                    imagen_url = row.get('IMAGEN')
                    if pd.notna(imagen_url) and imagen_url:
                        try:
                            self._download_and_set_product_image(product, imagen_url, sku)
                        except Exception as img_error:
                            logger.warning(f"⚠️ Error descargando imagen principal para {sku}: {str(img_error)}")
                    
                    # Procesar IMAGES (plural) - crear en modelo Images y asociar
                    images_url = row.get('IMAGES')
                    if pd.notna(images_url) and images_url:
                        try:
                            # Puede ser una URL o varias separadas por coma/pipe
                            urls = str(images_url).split('|') if '|' in str(images_url) else [images_url]
                            for idx, url in enumerate(urls):
                                url = url.strip()
                                if url:
                                    self._download_and_associate_image(product, url, f"{sku}-{idx+1}")
                        except Exception as img_error:
                            logger.warning(f"⚠️ Error descargando imágenes adicionales para {sku}: {str(img_error)}")
                    
                    if created:
                        stats['created'] += 1
                    else:
                        if producto_existente and producto_existente.is_removed and self.import_mode == 'soft_delete':
                            stats['reactivated'] += 1
                        else:
                            stats['updated'] += 1
                except Exception as e:
                    stats['errors'] += 1
                    logger.warning(f"⚠️ Error procesando fila {index}: {str(e)}")
            
            # Marcar como procesado
            self.uploaded = True
            # Usar update para evitar recursión infinita
            ImportFile.objects.filter(pk=self.pk).update(uploaded=True)
            
            logger.info(f"✅ Importación completada: {stats['created']} creados, {stats['updated']} actualizados, {stats['reactivated']} reactivados, {stats['errors']} errores")
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error en importación: {str(e)}", exc_info=True)
            raise
    
    def _download_and_set_product_image(self, product, image_url, sku):
        """
        Descarga una imagen y la guarda directamente en el campo image del producto
        """
        import requests
        from django.core.files.base import ContentFile
        import os
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # Limpiar URL
            image_url = str(image_url).strip()
            
            # Descargar imagen
            logger.info(f"📥 Descargando imagen principal para {sku}: {image_url}")
            response = requests.get(image_url, timeout=30, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            
            # Obtener extensión del archivo
            content_type = response.headers.get('content-type', '')
            if 'image/jpeg' in content_type or 'image/jpg' in content_type:
                ext = 'jpg'
            elif 'image/png' in content_type:
                ext = 'png'
            elif 'image/webp' in content_type:
                ext = 'webp'
            else:
                ext = os.path.splitext(image_url)[1].lower().replace('.', '') or 'jpg'
            
            # Nombre del archivo
            filename = f"{sku}.{ext}"
            
            # Guardar directamente en el campo image del producto
            product.image.save(filename, ContentFile(response.content), save=True)
            logger.info(f"✅ Imagen principal guardada para {sku}")
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"⚠️ Error de red descargando imagen {image_url}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"❌ Error procesando imagen principal para {sku}: {str(e)}")
            raise
    
    def _download_and_associate_image(self, product, image_url, sku):
        """
        Descarga una imagen desde URL y la asocia al producto
        """
        import requests
        from django.core.files.base import ContentFile
        from django.core.files.storage import default_storage
        import os
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # Limpiar URL
            image_url = str(image_url).strip()
            
            # Descargar imagen
            logger.info(f"📥 Descargando imagen para {sku}: {image_url}")
            response = requests.get(image_url, timeout=30, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            
            # Obtener extensión del archivo
            content_type = response.headers.get('content-type', '')
            if 'image/jpeg' in content_type or 'image/jpg' in content_type:
                ext = 'jpg'
            elif 'image/png' in content_type:
                ext = 'png'
            elif 'image/webp' in content_type:
                ext = 'webp'
            else:
                # Intentar obtener de la URL
                ext = os.path.splitext(image_url)[1].lower().replace('.', '') or 'jpg'
            
            # Nombre del archivo
            filename = f"{sku}.{ext}"
            
            # Verificar si ya existe una imagen con este código
            existing_image = Images.objects.filter(
                code=sku,
                organization=self.catalogue.organization
            ).first()
            
            if existing_image:
                # Actualizar imagen existente
                existing_image.image.save(filename, ContentFile(response.content), save=True)
                logger.info(f"✅ Imagen actualizada para {sku}")
                image_obj = existing_image
            else:
                # Crear nueva imagen
                image_obj = Images.objects.create(
                    name=f"Imagen {product.name}",
                    code=sku,
                    alt=product.name,
                    organization=self.catalogue.organization
                )
                image_obj.image.save(filename, ContentFile(response.content), save=True)
                logger.info(f"✅ Imagen creada para {sku}")
            
            # Asociar imagen al producto si no está ya asociada
            if not product.images.filter(id=image_obj.id).exists():
                product.images.add(image_obj)
                logger.info(f"🔗 Imagen asociada al producto {sku}")
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"⚠️ Error de red descargando imagen {image_url}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"❌ Error procesando imagen para {sku}: {str(e)}")
            raise

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

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

# Modelo de Catálogo
class Catalogue(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name=_('name'))
    code = models.CharField(
        max_length=50,
        null=True,  # Temporal para migración
        blank=True,
        verbose_name=_('code'),
        help_text=_('Código único para identificar el catálogo (ej: CAT001, VERANO2026)'))
    slug = models.SlugField(
        max_length=255,
        verbose_name=_('slug'))
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('description'))
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='catalogues',
        verbose_name=_('organization'))
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('is active'),
        help_text=_('Indica si el catálogo está activo'))
    currency = models.CharField(
        max_length=10,
        choices=CURRENCY,
        blank=True,
        null=True,
        default='CLP',
        verbose_name=_('currency'))
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('created at'))
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('updated at'))

    class Meta:
        verbose_name = _('catalogue')
        verbose_name_plural = _('catalogues')
        ordering = ['organization', 'name']
        unique_together = [['slug', 'organization'], ['code', 'organization']]

    def __str__(self):
        return f"{self.organization.name} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

# Modelo Slide
class Slide(BaseModel):
    catalogue = models.ForeignKey(
        'Catalogue',
        on_delete=models.CASCADE,
        related_name='slides',
        null=True,  # Temporal para migración
        blank=True,
        verbose_name=_('catalogue'))
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

# Modelo de Configuración del Cliente
class ClientConfiguration(TimeStampedModel, SoftDeletableModel):
    catalogue = models.ForeignKey(
        'Catalogue',
        on_delete=models.CASCADE,
        related_name='client_configurations',
        null=True,  # Temporal para migración
        blank=True,
        verbose_name=_('catalogue'))
    name = models.CharField(
        max_length=100, 
        unique=True, 
        verbose_name=_('client name'),
        help_text="Nombre del cliente"
    )
    primary_color = models.CharField(
        max_length=7, 
        default="#FFFFFF", 
        verbose_name=_('primary color'),
        help_text="Color principal en formato hexadecimal, ej. #FF5733"
    )
    secondary_color = models.CharField(
        max_length=7, 
        default="#000000", 
        verbose_name=_('secondary color'),
        help_text="Color secundario en formato hexadecimal"
    )
    accent_color = models.CharField(
        max_length=7, 
        default="#007BFF", 
        verbose_name=_('accent color'),
        help_text="Color de acento en formato hexadecimal",
        blank=True,
        null=True
    )
    logo = models.ImageField(
        upload_to='client_configs/logos/', 
        blank=True, 
        null=True, 
        verbose_name=_('logo'),
        help_text="Logo del cliente"
    )
    favicon = models.ImageField(
        upload_to='client_configs/favicons/', 
        blank=True, 
        null=True,
        verbose_name=_('favicon'),
        help_text="Favicon del cliente"
    )
    domain = models.CharField(
        max_length=255, 
        unique=True, 
        verbose_name=_('domain'),
        help_text="Dominio o subdominio del cliente (ej. cliente.dominio.com)"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('description'),
        help_text="Descripción del cliente"
    )
    metadata = models.JSONField(
        blank=True,
        null=True,
        default=dict,
        verbose_name=_('metadata'),
        help_text="Información adicional en formato JSON"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('is active'),
        help_text="Indica si la configuración está activa"
    )

    class Meta:
        verbose_name = _('client configuration')
        verbose_name_plural = _('client configurations')
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Validar formato de colores hexadecimales
        for color_field in ['primary_color', 'secondary_color', 'accent_color']:
            color_value = getattr(self, color_field)
            if color_value and not color_value.startswith('#'):
                setattr(self, color_field, f'#{color_value}')
        super().save(*args, **kwargs)

# Señales
@receiver(post_save, sender=Product)
@prevent_recursion
def update_stock_status(sender, instance=None, created=False, **kwargs):
    """
    Actualiza automáticamente el stock_status cuando stock_quantity cambia
    - Si stock_quantity = 0 → stock_status = 'outofstock'
    - Si stock_quantity > 0 y manage_stock = True → stock_status = 'instock'
    """
    if instance and instance.manage_stock:
        # Determinar el nuevo estado
        new_status = None
        if instance.stock_quantity == 0:
            new_status = 'outofstock'
        elif instance.stock_quantity > 0 and instance.stock_status == 'outofstock':
            # Si había stock agotado y ahora hay stock, cambiar a instock
            new_status = 'instock'
        
        # Actualizar solo si cambió el estado
        if new_status and instance.stock_status != new_status:
            instance.stock_status = new_status
            instance.save(update_fields=['stock_status'])


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
