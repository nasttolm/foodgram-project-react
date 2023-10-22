# Generated by Django 4.2.6 on 2023-10-16 20:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0007_shoppingcart_recipe_cooking_time_delete_shopinglist_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='favourite',
            name='recipe',
        ),
        migrations.RemoveField(
            model_name='favourite',
            name='user',
        ),
        migrations.RemoveConstraint(
            model_name='shoppingcart',
            name='unique_shopping_cart',
        ),
        migrations.RemoveField(
            model_name='shoppingcart',
            name='recipe',
        ),
        migrations.AddField(
            model_name='shoppingcart',
            name='content_type',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='shoppingcart',
            name='object_id',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='shoppingcart',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddConstraint(
            model_name='shoppingcart',
            constraint=models.UniqueConstraint(fields=('user', 'object_id', 'content_type'), name='unique_shopping_cart_user_content_type_object_id'),
        ),
        migrations.DeleteModel(
            name='Favourite',
        ),
    ]
