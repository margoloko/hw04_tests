# Generated by Django 2.2.19 on 2021-11-17 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_auto_20211117_2248'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='slug',
            field=models.SlugField(max_length=190, unique=True),
        ),
    ]