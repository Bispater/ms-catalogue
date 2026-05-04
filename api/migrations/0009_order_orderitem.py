from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_alter_catalogueplaylist_start_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('is_removed', models.BooleanField(default=False)),
                ('external_transaction_id', models.CharField(help_text='`{terminal_id}-{operation_number}-{accounting_date}` u otro identificador único provisto por el cliente.', max_length=120, unique=True, verbose_name='external transaction id')),
                ('local_order_number', models.CharField(blank=True, help_text='Número impreso en el voucher (ej. 4 dígitos).', max_length=20, null=True, verbose_name='local order number')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('voided', 'Voided'), ('failed', 'Failed')], default='approved', max_length=20, verbose_name='status')),
                ('currency', models.CharField(choices=[('CLP', 'Peso Chileno (CLP)'), ('USD', 'Dólar Estadounidense (USD)'), ('EUR', 'Euro (EUR)'), ('ARS', 'Peso Argentino (ARS)'), ('BRL', 'Real Brasileño (BRL)'), ('MXN', 'Peso Mexicano (MXN)'), ('COP', 'Peso Colombiano (COP)'), ('PEN', 'Sol Peruano (PEN)')], default='CLP', max_length=10, verbose_name='currency')),
                ('subtotal', models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='subtotal')),
                ('total', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='total')),
                ('authorization_code', models.CharField(blank=True, help_text='Código de autorización Transbank (impreso en el voucher).', max_length=20, null=True, verbose_name='authorization code')),
                ('operation_number', models.CharField(blank=True, max_length=40, null=True, verbose_name='operation number')),
                ('terminal_id', models.CharField(blank=True, max_length=40, null=True, verbose_name='terminal id')),
                ('commerce_code', models.CharField(blank=True, max_length=40, null=True, verbose_name='commerce code')),
                ('card_type', models.CharField(blank=True, choices=[('CR', 'Credit'), ('DB', 'Debit'), ('PR', 'Prepaid')], max_length=2, null=True, verbose_name='card type')),
                ('card_brand', models.CharField(blank=True, max_length=40, null=True, verbose_name='card brand')),
                ('last_4_digits', models.CharField(blank=True, max_length=4, null=True, verbose_name='last 4 digits')),
                ('accounting_date', models.CharField(blank=True, help_text='Fecha contable Transbank (formato MMDD o YYYYMMDD según el POS).', max_length=10, null=True, verbose_name='accounting date')),
                ('real_date', models.CharField(blank=True, max_length=10, null=True, verbose_name='real date')),
                ('real_time', models.CharField(blank=True, max_length=10, null=True, verbose_name='real time')),
                ('response_code', models.CharField(blank=True, max_length=10, null=True, verbose_name='response code')),
                ('response_message', models.TextField(blank=True, null=True, verbose_name='response message')),
                ('ticket', models.CharField(blank=True, help_text='Identificador del ticket que el totem envió al POS al iniciar la venta.', max_length=60, null=True, verbose_name='ticket')),
                ('raw_response', models.JSONField(blank=True, help_text='Respuesta completa del POS, guardada para depuración / conciliación.', null=True, verbose_name='raw response')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='notes')),
                ('catalogue', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='orders', to='api.catalogue', verbose_name='catalogue')),
            ],
            options={
                'verbose_name': 'order',
                'verbose_name_plural': 'orders',
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_snapshot', models.CharField(max_length=250, verbose_name='product name snapshot')),
                ('sku_snapshot', models.CharField(blank=True, max_length=250, null=True, verbose_name='sku snapshot')),
                ('quantity', models.PositiveIntegerField(default=1, verbose_name='quantity')),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='unit price')),
                ('line_total', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='line total')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='api.order', verbose_name='order')),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='order_items', to='api.product', verbose_name='product')),
            ],
            options={
                'verbose_name': 'order item',
                'verbose_name_plural': 'order items',
                'ordering': ['id'],
            },
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['catalogue', '-created'], name='api_order_catalog_e6d9c5_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['authorization_code'], name='api_order_authori_8c98ad_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['terminal_id', 'accounting_date'], name='api_order_termina_4f8b3c_idx'),
        ),
    ]
