# Generated by Django 4.2.17 on 2025-01-08 17:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service_center_app', '0006_sparepart_created_at_sparepart_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='name',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='client',
            name='phone',
            field=models.CharField(default='+375 (29) XXX-XX-XX', max_length=20),
        ),
    ]
