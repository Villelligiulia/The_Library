# Generated by Django 3.2.20 on 2023-09-09 14:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0003_alter_book_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='cover_image',
            field=models.ImageField(default='book_covers/default.jpg', upload_to='media'),
        ),
    ]