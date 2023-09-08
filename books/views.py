from django.shortcuts import render, redirect, redirect, get_object_or_404, reverse
from .models import Book, Category, Author
from django.contrib import messages
from django.db.models import Q
from .forms import ReviewForm
from django.db.models import Avg
from .forms import BookForm, BookFormEdit
from django.contrib.auth.decorators import login_required


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


def book_detail(request, book_id):
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
    return render(request, 'books/book_detail.html', {'book': book, 'review_form': review_form, })


def all_categories(request):

    categorys = Category.objects.order_by('name')
    context = {
        'categorys': categorys,

    }
    return render(request, 'books/all-categories.html', context)


def best_sellers(request):
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
    books = Book.objects.all()
    return render(request, 'books/library_management.html', {'books': books})


@login_required
def create_book(request):
    if not request.user.is_superuser:
        messages.error(request, "Sorry only the Library has access to this service")
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
                    request, f"A book '{title}' by {author_name} already exists in the library.")
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
                request, f"{book.title} by {author_name}, has been added to your Library'.")

            new_book_detail_url = reverse('book_detail', args=[book.id])

            # Redirect to the book detail page
            return redirect(new_book_detail_url)
    else:
        form = BookForm()
    return render(request, 'books/create_book.html', {'form': form})


@login_required
def edit_book(request, book_id):

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
    return render(request, 'books/edit_book.html', {'form': form, 'book': book})


def admin_search_book(request):
    query = request.GET.get('q')
    books = Book.objects.all()

    if not query:
        messages.warning(request, 'Please enter a search term.')
        return redirect('library_management')

    admin_searched_books = books.filter(Q(title__icontains=query) | Q(
        author__name__icontains=query))

    if not admin_searched_books:
        messages.warning(request, f"No books found for '{query}'.")

    context = {
        'books': admin_searched_books,
    }

    return render(request, 'books/library_management.html', context)


@login_required
def delete_book(request, book_id):
    if not request.user.is_superuser:
        messages.error(
            request, "Sorry only the Library has access to this service")
        return redirect(reverse('book_list'))

    
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        book.delete()
        messages.success(
            request, f"{book.title} by {book.author}, has been removed from the Library'.")
        return redirect('library_management')
    return render(request, 'books/delete_book.html', {'book': book, })


