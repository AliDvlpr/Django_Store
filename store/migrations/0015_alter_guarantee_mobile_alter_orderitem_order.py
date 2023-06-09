# Generated by Django 4.1.5 on 2023-01-12 10:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0014_guarantee_activated_date_guarantee_created_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='guarantee',
            name='mobile',
            field=models.CharField(blank=True, max_length=13),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='items', to='store.order'),
        ),
    ]
