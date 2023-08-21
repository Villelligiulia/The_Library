from django.shortcuts import render, redirect
from .models import Book, Category, Author
from django.contrib import messages
from django.db.models import Q


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


def search_book(request):
    query = request.GET.get('q')
    books = Book.objects.all()

    if not query:
        messages.warning(request, 'Please enter a search term.')
        return redirect('book_list')

    searched_books = books.filter(Q(title__icontains=query) | Q(
        author__name__icontains=query) | Q(category__name__icontains=query))

    if not searched_books:
        messages.warning(request, f"No books found for '{query}'.")

    context = {
        'books': searched_books,
    }

    return render(request, 'books/book_list.html', context)
