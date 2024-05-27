from django.shortcuts import render, redirect
from inventory.models import *


def home(request):
    shop = ProductInventory.objects.prefetch_related("media_product_inventory").all()

    if request.method == "POST":
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')
        print(product_id)

        # Retrieve the cart from the session, defaulting to an empty dictionary if it doesn't exist
        cart = request.session.get('cart', {})

        if product_id in cart:
            cart[product_id] += int(quantity)
        else:
            cart[product_id] = int(quantity)

        # Save the updated cart back to the session
        request.session['cart'] = cart
    
    cart = request.session.get('cart', {})
    print(request.session.get('cart',{}))
    cart_items = []
    total_price = 0

    for product_id, quantity in cart.items():
        product = ProductInventory.objects.prefetch_related("media_product_inventory").filter(pk=product_id).first()
            
        if product:
            item_total = product.retail_price * int(quantity)
            product_name = product.product.name
            media_info = [{'url': media.image, 'alt_text': media.alt_text} for media in product.media_product_inventory.all()]

                      
        total_price += item_total
        print(product)

        cart_items.append({
                'product': product,
                'quantity': quantity,
                'item_total': item_total,
                'image': product,
                'product_name':product_name,
                'media_info':media_info

            })
        print(cart_items)

    context = {
        'products': shop,
        'cart_items': cart_items,
        'total_price': total_price
    }
    
    return render(request, "inventory/cart.html",context)




def checkout(request):
    return render(request, "inventory/checkout.html")
