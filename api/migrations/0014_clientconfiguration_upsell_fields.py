from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_split_metadata_namespaces'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientconfiguration',
            name='upsell_enabled',
            field=models.BooleanField(
                default=False,
                help_text='Mostrar tarjeta de sugerencia en el carrito',
                verbose_name='upsell enabled',
            ),
        ),
        migrations.AddField(
            model_name='clientconfiguration',
            name='upsell_product',
            field=models.ForeignKey(
                blank=True,
                help_text='Producto sugerido al cliente al revisar el carrito',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='upsell_configurations',
                to='api.product',
                verbose_name='upsell product',
            ),
        ),
        migrations.AddField(
            model_name='clientconfiguration',
            name='upsell_title',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Encabezado de la sugerencia, e.g. "¿Sumas un shot?"',
                max_length=120,
                verbose_name='upsell title',
            ),
        ),
        migrations.AddField(
            model_name='clientconfiguration',
            name='upsell_description',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Texto corto de la sugerencia (incluye el precio si quieres mostrarlo)',
                max_length=255,
                verbose_name='upsell description',
            ),
        ),
        migrations.AddField(
            model_name='clientconfiguration',
            name='upsell_price',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Precio especial al agregar desde la sugerencia (vacío = precio del producto)',
                max_digits=12,
                null=True,
                verbose_name='upsell price',
            ),
        ),
        migrations.AddField(
            model_name='clientconfiguration',
            name='upsell_cta_label',
            field=models.CharField(
                blank=True,
                default='Sumar',
                help_text='Texto del botón, e.g. "Sumar"',
                max_length=32,
                verbose_name='upsell CTA label',
            ),
        ),
    ]
