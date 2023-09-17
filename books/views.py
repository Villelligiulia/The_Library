from django.shortcuts import render, redirect, get_object_or_404, reverse
from .models import Book, Category, Author
from django.contrib import messages
from django.db.models import Q
from .forms import ReviewForm
from django.db.models import Avg
from .forms import BookForm, BookFormEdit
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator


def custom_404_view(request, exception):
    return render(request, '404.html', {})


def book_list(request):
    """
    Display a list of books, optionally filtered by category.
    Allow 18 books per page via paginator.
    """
    book_queryset = Book.objects.all()
    books = Book.objects.all()
    items_per_page = 18
    paginator = Paginator(books, items_per_page)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    lowest_priced_books = Book.objects.order_by('price')[:5]
    categories = Category.objects.all()
    selected_category = request.GET.get('category')
    show_picture = True

    if selected_category:
        page = Book.objects.filter(category__name=selected_category)
    else:
        book = book_queryset

    context = {
        'books': books,
        'lowest_priced_books': lowest_priced_books,
        'categories': categories,
        'selected_category': selected_category,
        'show_picture': show_picture,
        'page': page,


    }

    return render(request, 'books/book_list.html', context)


def search_book(request):
    """
    Search for books based on a query string.
    """
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
        'page': searched_books,
    }

    return render(request, 'books/book_list.html', context)


def book_detail(request, book_id):
    """
    Display details of a specific book, including reviews.
    Allow users to submit reviews.
    """
    book = get_object_or_404(Book, id=book_id)
    review_form = ReviewForm(request.POST or None)
    if request.method == 'POST':
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.user = request.user
            review.book = book
            review.save()
            messages.success(request, 'Your review has been submitted.')
            return redirect('book_detail', book_id=book_id)
    return render(request, 'books/book_detail.html', {'book': book,
                                                      'review_form':
                                                          review_form, })


def all_categories(request):
    """
    Display books categories
    """

    categorys = Category.objects.order_by('name')
    context = {
        'page': categorys,




    }
    return render(request, 'books/all-categories.html', context)


def best_sellers(request):
    """
    Display best seller books and lowest price books
    """
    lowest_priced_books = Book.objects.order_by('price')[:7]
    best_seller_books = Book.objects.annotate(
        avg_rating=Avg('ratings')).order_by('-avg_rating')[:21]
    context = {
        'best_seller_books': best_seller_books,
        'lowest_priced_books': lowest_priced_books,
    }
    return render(request, 'books/best_sellers.html', context)


@login_required
def library_management(request):
    """
    Display book list to perform admin actions
    """
    books = Book.objects.all()
    books = Book.objects.all()
    items_per_page = 18
    paginator = Paginator(books, items_per_page)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'books/library_management.html', {'books': books,
                                                             'page': page})


@login_required
def create_book(request):
    """
    Allow to create a new book if user is admin
    """
    if not request.user.is_superuser:
        messages.error(
            request, "Sorry only the Library has access to this service")
        return redirect(reverse('book_list'))

    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            # Extract the author name from the form
            author_name = form.cleaned_data['author_name']
            title = form.cleaned_data['title']

            # Check if a book with the same title and author already exists
            existing_book = Book.objects.filter(
                title=title, author__name=author_name).first()

            if existing_book:
                messages.error(
                    request, f"A book '{title}' by {author_name} already\
                    exists in the library.")
                return redirect('create_book')

            # Save the form without the author_name field
            book = form.save(commit=False)

            # Check if the book's author already exists in the database
            author = None
            if author_name:
                author = Book.objects.filter(author__name=author_name).first()

            # Create a new author entry if it doesn't exist
            if not author:
                from .models import Author
                author = Author.objects.create(name=author_name)

            # Link the book to the author and save
            book.author = author
            book.save()
            messages.success(
                request, f"{book.title} by {author_name}, has been added to\
                           your Library.")

            new_book_detail_url = reverse('book_detail', args=[book.id])

            # Redirect to the book detail page
            return redirect(new_book_detail_url)
    else:
        form = BookForm()
    return render(request, 'books/create_book.html', {'form': form})


@login_required
def edit_book(request, book_id):
    """
    Allow to edit books if user is admin
    """

    if not request.user.is_superuser:
        messages.error(
            request, "Sorry only the Library has access to this service")
        return redirect(reverse('book_list'))

    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        form = BookFormEdit(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            return redirect('library_management')
    else:
        form = BookFormEdit(instance=book)
    return render(request, 'books/edit_book.html', {'form': form,
                                                    'book': book})


def admin_search_book(request):
    """
    Perform book search filtered by book title category or author for
    library management
    """
    query = request.GET.get('q')
    books = Book.objects.all()

    if not query:
        messages.warning(request, 'Please enter a search term.')
        return redirect('library_management')

    admin_searched_books = books.filter(Q(title__icontains=query) | Q(
        author__name__icontains=query) | Q(category__name__icontains=query))

    if not admin_searched_books:
        messages.warning(request, f"No books found for '{query}'.")

    context = {
        'page': admin_searched_books,
    }

    return render(request, 'books/library_management.html', context)


@login_required
def delete_book(request, book_id):
    """
    Allow to delete books if user is admin
    """
    if not request.user.is_superuser:
        messages.error(
            request, "Sorry only the Library has access to this service")
        return redirect(reverse('book_list'))

    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        book.delete()
        messages.success(
            request, f"{book.title} by {book.author}, has been removed from\
                       the Library.")
        return redirect('library_management')
    return render(request, 'books/delete_book.html', {'book': book, })
