from decimal import Decimal
from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from books.models import Book

# Create your views here.

CART_SESSION_KEY = 'cart'


def get_cart(request):
    """
    Retrieve the current shopping cart from the user's session.
    """
    cart = request.session.get(CART_SESSION_KEY, {})
    return cart


def save_cart(request, cart):
    """
    Save the updated shopping cart back to the user's session.
    """
    request.session[CART_SESSION_KEY] = cart
    request.session.modified = True


def add_to_cart(request, book_id):
    """
    Add a book to the shopping cart or update its quantity if it
    already exists.
    """
    quantity = int(request.POST.get('quantity', 1))
    book = get_object_or_404(Book, id=book_id)

    cart = get_cart(request)
    cart_item = cart.get(str(book.id))

    if cart_item is None:
        cart_item = {
            'book_id': book.id,
            'title': book.title,
            'price': str(book.price),
            'quantity': quantity,
        }
    else:
        cart_item['quantity'] += quantity

    cart[str(book.id)] = cart_item
    save_cart(request, cart)

    messages.success(request, f"{book.title} has been added to your cart.")
    return redirect('view_cart')


def view_cart(request):
    """
    Display the contents of the shopping cart.
    """
    cart = get_cart(request)
    total_price = Decimal(0)
    items = []

    for item in cart.values():
        item['price'] = Decimal(item['price'])
        total_price += item['price'] * item['quantity']
        book = get_object_or_404(Book, id=item['book_id'])
        items.append({
            'book': book,
            'quantity': item['quantity'],
            'subtotal': item['price'] * item['quantity'],

        })

    context = {
        'items': items,
        'total_price': total_price,

    }

    return render(request, 'cart/view_cart.html', context)


def remove_from_cart(request, book_id):
    """
     Remove a book from the shopping cart.
     """
    book_id = str(book_id)

    cart = get_cart(request)
    cart_item = cart.get(book_id)

    if cart_item:
        del cart[book_id]
        save_cart(request, cart)
        messages.success(
            request, f"{cart_item['title']} has been removed from your cart.")
    else:
        messages.info(request, "Item is not in your cart.")

    return redirect('view_cart')
