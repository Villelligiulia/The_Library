from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404, reverse
from checkout.forms import CheckoutForm
from checkout.models import Order, OrderLineItem
from decimal import Decimal
from books.models import Book
from django.conf import settings
from django.http import HttpResponse


def checkout(request):

    # Check if the cart is empty
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(
            request, 'At the moment our cart is empty. Please add items to your cart.')
        return redirect('book_list')

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
                # Save the checkout form data
                # checkout_first_name=form.cleaned_data['first_name'],
                # checkout_last_name=form.cleaned_data['last_name'],
                # checkout_email=form.cleaned_data['email'],
                # checkout_address=form.cleaned_data['address'],
                # checkout_city=form.cleaned_data['city'],
                # checkout_state=form.cleaned_data['state'],
                # checkout_country=form.cleaned_data['country'],
                # checkout_postal_code=form.cleaned_data['postal_code'],
                # checkout_save_to_profile=save_to_profile,




            )
        order.save()

    else:

        initial_data = {

        }
        # Retrieve previously saved checkout information from the session
        # saved_checkout_info = request.session.get('checkout_info', {})
        # if saved_checkout_info:
        #     initial_data.update(saved_checkout_info)

        form = CheckoutForm(initial_data=initial_data)

        context = {
            'form': form,
            'cart_items': items,





        }
        return render(request, 'checkout/checkout.html', context)
