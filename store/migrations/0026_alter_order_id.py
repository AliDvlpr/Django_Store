# Generated by Django 4.1.5 on 2023-02-13 08:47

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0025_alter_order_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='id',
            field=models.UUIDField(default=uuid.uuid3, primary_key=True, serialize=False),
        ),
    ]
