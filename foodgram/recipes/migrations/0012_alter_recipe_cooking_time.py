# Generated by Django 4.2.6 on 2023-10-30 14:14

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0011_alter_tag_color'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1, message='Время должно быть больше 1 минуты'), django.core.validators.MaxValueValidator(30000, message='Время  не должно быть больше 30000 минут')], verbose_name='Время приготовления в минутах'),
        ),
    ]