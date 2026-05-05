from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_order_orderitem'),
    ]

    operations = [
        migrations.CreateModel(
            name='Terminal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('code', models.CharField(help_text='Identificador del totem definido por el operador (ej: TOTEM-01).', max_length=60, verbose_name='terminal code')),
                ('pos_terminal_id', models.CharField(blank=True, help_text='ID del POS reportado por Transbank (ej: IM750308).', max_length=40, null=True, verbose_name='pos terminal id')),
                ('commerce_code', models.CharField(blank=True, max_length=40, null=True, verbose_name='commerce code')),
                ('port', models.CharField(blank=True, help_text='Puerto USB serial (ej: COM5).', max_length=40, null=True, verbose_name='serial port')),
                ('connected', models.BooleanField(default=False, verbose_name='connected')),
                ('keys_loaded', models.BooleanField(default=False, verbose_name='keys loaded')),
                ('last_state', models.CharField(choices=[('IDLE', 'Idle'), ('INICIANDO_PAGO', 'Iniciando pago'), ('ESPERANDO_TARJETA', 'Esperando tarjeta'), ('PROCESANDO', 'Procesando'), ('APROBADO', 'Aprobado'), ('RECHAZADO', 'Rechazado'), ('CANCELADO', 'Cancelado'), ('ERROR', 'Error'), ('OFFLINE', 'Offline')], default='OFFLINE', max_length=30, verbose_name='last state')),
                ('last_state_message', models.TextField(blank=True, null=True, verbose_name='last state message')),
                ('last_heartbeat_at', models.DateTimeField(blank=True, help_text='Última vez que el servicio del totem reportó.', null=True, verbose_name='last heartbeat at')),
                ('last_poll_at', models.DateTimeField(blank=True, help_text='Última vez que el servicio hizo poll al POS.', null=True, verbose_name='last poll at')),
                ('service_version', models.CharField(blank=True, max_length=40, null=True, verbose_name='service version')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='notes')),
                ('catalogue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='terminals', to='api.catalogue', verbose_name='catalogue')),
            ],
            options={
                'verbose_name': 'terminal',
                'verbose_name_plural': 'terminals',
                'ordering': ['catalogue', 'code'],
                'unique_together': {('catalogue', 'code')},
            },
        ),
    ]
