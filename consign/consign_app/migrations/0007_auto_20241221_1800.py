# Generated by Django 3.0 on 2024-12-21 12:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('consign_app', '0006_gdmtemp'),
    ]

    operations = [
        migrations.RenameField(
            model_name='addconsignment',
            old_name='delivery_type',
            new_name='collection_type',
        ),
    ]
