from decimal import Decimal
from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from books.models import Book

# Create your views here.

CART_SESSION_KEY = 'cart'


def get_cart(request):
    cart = request.session.get(CART_SESSION_KEY, {})
    return cart


def save_cart(request, cart):
    request.session[CART_SESSION_KEY] = cart
    request.session.modified = True


def add_to_cart(request, book_id):
    # Default quantity to 1 if not provided
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
