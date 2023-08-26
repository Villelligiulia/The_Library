import os
import stripe

from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404, reverse
from checkout.forms import CheckoutForm
from checkout.models import Order, OrderLineItem
from decimal import Decimal
from books.models import Book
from django.conf import settings
from django.http import HttpResponse
from cart.context import cart_content


def checkout(request):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    # Check if the cart is empty
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(
            request, 'At the moment our cart is empty. Please add items to your cart.')
        return redirect('book_list')

    current_cart = cart_content(request)
    total = current_cart['total_price']
    stripe_total = round(total * 100)
    stripe.api_key = stripe_secret_key
    intent = stripe.PaymentIntent.create(
        amount=stripe_total,
        currency=settings.STRIPE_CURRENCY,
    )
    print(intent)

    # Retrieve cart items and total price
    items = []
    total_price = Decimal(0)
    for item in cart.values():
        item['price'] = Decimal(item['price'])
        total_price += item['price'] * item['quantity']
        book = get_object_or_404(Book, id=item['book_id'])
        items.append({
            'book': book,
            'quantity': item['quantity'],
            'subtotal': item['price'] * item['quantity'],
        })

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            save_to_profile = form.cleaned_data['save_to_profile']

            if save_to_profile:

                request.session['checkout_info'] = form.cleaned_data

            else:
                request.session['checkout_info'] = None

            order = Order(
                user=request.user,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                address=form.cleaned_data['address'],
                city=form.cleaned_data['city'],
                state=form.cleaned_data['state'],
                country=form.cleaned_data['country'],
                postal_code=form.cleaned_data['postal_code'],
                save_to_profile=save_to_profile,






            )
        order.save()
        for item in items:
            book = item['book']
            quantity = item['quantity']
            OrderLineItem.objects.create(
                order=order, book=book, quantity=quantity)

        # Clear the cart
        request.session['cart'] = {}

    # Redirect the user to the to checkout_success after successful checkout
        return redirect(reverse('checkout_success', args=[order.order_number]))

    else:

        initial_data = {

        }

        form = CheckoutForm(initial_data=initial_data)

        context = {
            'form': form,
            'cart_items': items,
            'stripe_public_key': stripe_public_key,
            'client_secret': intent.client_secret,





        }
        return render(request, 'checkout/checkout.html', context)


def checkout_success(request, order_number):
    """
    Handle successful checkouts
    """
    save_info = request.session.get('save_info')
    order = get_object_or_404(Order, order_number=order_number)
    messages.success(request, f'Order successfully processed! \
        Thank you for shopping with us !!')

    if 'cart' in request.session:
        del request.session['cart']

    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
        'save_to_profile': order.save_to_profile,
    }

    return render(request, template, context)
