# Generated by Django 4.1.7 on 2023-03-07 07:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0031_alter_group_image_alter_news_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='laststatus',
            field=models.CharField(choices=[('P', 'Pending'), ('C', 'Complete'), ('F', 'Failed'), ('S', 'Sending'), ('R', 'Received')], default='P', max_length=1),
        ),
    ]
