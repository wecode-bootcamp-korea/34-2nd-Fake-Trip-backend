# Generated by Django 4.0.5 on 2022-07-05 18:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Product_image',
            new_name='ProductImage',
        ),
        migrations.RenameModel(
            old_name='Room_image',
            new_name='RoomImage',
        ),
    ]