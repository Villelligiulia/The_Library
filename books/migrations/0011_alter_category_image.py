# Generated by Django 3.2.20 on 2023-09-10 04:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0010_alter_category_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='image',
            field=models.ImageField(default='default.jpg', upload_to='media/category_images'),
        ),
    ]
