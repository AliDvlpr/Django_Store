# Generated by Django 3.2.12 on 2023-04-19 08:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0037_auto_20230319_0641'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='laststatus',
        ),
    ]
