from django.shortcuts import render

# Create your views here.


def book_list(request):
    """ A view to return the index page """

    return render(request, 'books/book-list.html')
