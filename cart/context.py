from decimal import Decimal


def cart_content(request):
    cart = request.session.get('cart', {})
    total_price = get_total_price(cart)
    cart_items = []

    for item in cart.values():
        item['price'] = Decimal(item['price'])
        cart_items.append({
            'book_id': item['book_id'],
            'title': item['title'],
            'price': item['price'],
            'quantity': item['quantity'],
        })

    return {
        'cart_items': cart_items,
        'total_price': total_price,
    }

def total_price(request):
    cart = request.session.get('cart', {})
    total_price = get_total_price(cart)
    return {'total_price': total_price}

def get_total_price(cart):
    total_price = Decimal(0)
    for item in cart.values():
        item['price'] = Decimal(item['price'])
        total_price += item['price'] * item['quantity']
    return total_price