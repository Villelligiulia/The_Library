from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField


class Author(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(
        upload_to='category_images', default='default.jpg')

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    description = models.TextField(blank=False, null=True)
    price = models.DecimalField(
        max_digits=8, decimal_places=2, blank=False, null=False)
    cover_image = models.ImageField(
        upload_to='media/book_covers', default='media/default.jpg')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    ratings = models.DecimalField(max_digits=3, decimal_places=1)
    quantity = models.IntegerField(default=0)

    def __str__(self):
        return self.title


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # Reference the Book model
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} for {self.book.title}"
