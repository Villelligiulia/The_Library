from django.shortcuts import render
from .models import Book, Category


def book_list(request):
    book_queryset = Book.objects.all()
    lowest_priced_books = Book.objects.order_by('price')[:5]
    categories = Category.objects.all()
    selected_category = request.GET.get('category')
    show_picture = True

    if selected_category:
        books = Book.objects.filter(category__name=selected_category)
    else:
        books = book_queryset

    context = {
        'books': books,
        'lowest_priced_books': lowest_priced_books,
        'categories': categories,
        'selected_category': selected_category,
        'show_picture': show_picture,


    }

    return render(request, 'books/book_list.html', context)
