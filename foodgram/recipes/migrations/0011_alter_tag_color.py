# Generated by Django 4.2.6 on 2023-10-26 10:42

import colorfield.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0010_alter_tag_name_alter_tag_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=colorfield.fields.ColorField(blank=True, default='#FF0000', image_field=None, max_length=25, null=True, samples=None, verbose_name='Цвет в HEX'),
        ),
    ]