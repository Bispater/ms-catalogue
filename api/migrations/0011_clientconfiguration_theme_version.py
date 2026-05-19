from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_terminal'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientconfiguration',
            name='theme_version',
            field=models.CharField(
                choices=[
                    ('classic', 'Classic (diseño original)'),
                    ('v1-midnight', 'V1 Midnight (disco / nightclub)'),
                    ('v2-neon', 'V2 Neon After Hours'),
                    ('v3-vip', 'V3 VIP'),
                    ('v4-aurora', 'V4 Aurora'),
                ],
                default='classic',
                help_text='Versión visual aplicada en el totem (V1 Midnight, V2 Neon, etc.)',
                max_length=32,
                verbose_name='theme version',
            ),
        ),
    ]
