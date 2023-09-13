# Generated by Django 3.2.20 on 2023-09-13 07:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0015_alter_book_cover_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='cover_image',
            field=models.ImageField(default='/books/media/default.jpg', upload_to='book_covers'),
        ),
        migrations.AlterField(
            model_name='category',
            name='image',
            field=models.ImageField(default='/books/media/default.jpg', upload_to='category_images'),
        ),
    ]
