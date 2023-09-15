from django.contrib import admin

from .models import Category, Book, Review


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    pass


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    pass
