# Generated by Django 4.2.6 on 2023-10-12 19:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_achievement_achievementrecipe_achievementtag_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='description',
            field=models.TextField(blank=True, verbose_name='Описание рецепта'),
        ),
    ]
