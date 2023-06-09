# Generated by Django 4.1.7 on 2023-03-01 09:04

from django.db import migrations, models
import django.db.models.deletion
import store.validators


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0029_supertag_product_supertag'),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('slug', models.SlugField()),
                ('image', models.ImageField(upload_to='store/images', validators=[store.validators.validate_file_size])),
                ('description', models.TextField(blank=True, null=True)),
                ('last_update', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['title'],
            },
        ),
        migrations.DeleteModel(
            name='Supertag',
        ),
        migrations.RemoveField(
            model_name='collection',
            name='featured_product',
        ),
        migrations.RemoveField(
            model_name='product',
            name='collection',
        ),
        migrations.RemoveField(
            model_name='product',
            name='supertag',
        ),
        migrations.AddField(
            model_name='group',
            name='collection',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='groups', to='store.collection'),
        ),
        migrations.AddField(
            model_name='group',
            name='featured_product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='store.product'),
        ),
        migrations.AddField(
            model_name='collection',
            name='featured_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='store.group'),
        ),
        migrations.AddField(
            model_name='product',
            name='group',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='products', to='store.group'),
            preserve_default=False,
        ),
    ]
