from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
import logging
from django.shortcuts import render, get_object_or_404

from inventory.models import *
from .models import *


def dashboard(request):
    graph_data = ProductInventory.objects.all().order_by('id')

    context = {
        'graph_data': graph_data
    }
    return render(request, "dashboard/side.html", context)


def add_product(request):
    items = []
    products = ProductInventory.objects.all()
    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    for product in products:
        product_name = product.product.name
        price = product.retail_price
        product_description = product.product.description
        added_date = product.created_at
        active_status = product.is_active
        product_type = product.product_type
        brand = product.brand

        items.append({
            'product_name': product_name,
            'product_price': price,
            'product_description': product_description,
            'added_date': added_date,
            'active_status': active_status,
            'product_type': product_type,
            'brand': brand,
            'id':product.pk
        })

    context = {
        'items': items,
        'page_obj': page_obj
    }
    return render(request, "dashboard/products.html", context)


def orders(request):
    orders_collection = Order.objects.select_related('customer').all().order_by('-created_at')
    paginator = Paginator(orders_collection, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'orders': orders_collection,
        'page_obj': page_obj
    }
    return render(request, "dashboard/order.html", context)

@csrf_protect
@require_http_methods(["GET", "POST"])
def signin(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password")
            return redirect('signin')

    return render(request, "dashboard/sign_in.html")


def order_status(request, order_id):
    if request.method == 'POST':
        print(f"Attempting to update order with id: {order_id}")
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('status')
        if new_status:
            order.status = new_status
            order.save()

        return redirect('orders')

    return render(request, "dashboard/order_status.html", {'order': order_id})


def setting(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        status = request.POST.get('status')  # Assuming 'status' refers to whether the user is a staff member or not.
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists.')
            else:
                is_staff = True if status == 'on' else False  # Change 'on' based on the value sent from the form
                user = User.objects.create_user(username=username, email=email, password=password1, is_staff=is_staff)
                user.save()
                messages.success(request, 'User created successfully.')
                return redirect('setting')
        else:
            messages.error(request, 'Passwords do not match.')

    user_details = User.objects.all()
    context = {
        'user': user_details
    }
    return render(request, "dashboard/setting.html", context)


def inbox(request):
    msgs = ContactForm.objects.all()
    context = {
        'info': msgs
    }
    return render(request, "dashboard/inbox.html", context)


def categories(request):
    cate = Category.objects.all()
    edit_mode_is_valid = request.GET.get('mode') == "edit" and int(request.GET.get('id', 0)) != 0

    edit_info = {
            'edit_mode':edit_mode_is_valid,
            'cat_id':int(request.GET.get('id',0))
        }
    print(edit_info)

    if edit_mode_is_valid:
            cat = Category.objects.get(pk=edit_info['cat_id'])
            edit_info['category_info'] = cat
    print(edit_info)


    if request.method == "POST":
        category_id = request.POST.get('category_id')

        category_name = request.POST.get('name')
        safe_url = request.POST.get('slug')
        parent_id = request.POST.get('parent')
        status = request.POST.get('is_active')

        

        
        parent_category = None
        if parent_id:
            try:
                parent_category = Category.objects.get(id=parent_id)
            except Category.DoesNotExist:
                pass
        
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
                category.name = category_name
                category.slug = safe_url
                category.parent = parent_category
                category.is_active = status 
                category.save()
            except Category.DoesNotExist:
                pass
        else:
            category = Category(
                name=category_name,
                slug=safe_url,
                parent=parent_category,
                is_active=status
            )

            category.save()

    context = {
        'items': cate,
        'edit_info':edit_info
    }
    return render(request, "dashboard/categories.html", context)


def stocks(request):
    cate = Stock.objects.all()
    context = {
        'items': cate
    }
    return render(request, "dashboard/stocks.html", context)


def notification(request):
    notify = Notification.objects.all()

    context = {
        'notify': notify
    }
    return render(request, "dashboard/notification.html", context)


def invoice(request):
    """
    Handle invoice generation and order status update.
    GET: Display invoice form
    POST: Update order status and fetch invoice data
    """
    order_data = None
    customer_data = None
    total_amount = 0

    if request.method == "POST":
        order_keys = request.POST.get('order_id')
        cust_key = request.POST.get('customer_id')

        print("Debug info:", order_keys, cust_key)

        try:
            order_data = get_object_or_404(Order, pk=order_keys)
            customer_data = get_object_or_404(Customer, pk=cust_key)

            total_amount = order_data.total_price * order_data.item_count

            print(order_data)
        except Exception as e:
            return HttpResponse(f"Error fetching data: {str(e)}", status=400)

    context = {
        'order': order_data,
        'customer': customer_data,
        'amount': total_amount
    }

    return render(request, "dashboard/invoice.html", context)


def add(request):
    categories_p = Category.objects.filter(is_active=True)
    product = Product.objects.all()
    brand = Brand.objects.all()
    product_type = ProductType.objects.all()
    product_inventory = ProductInventory.objects.all()
    edit_mode_valid = request.GET.get('mode') == "edit" and int(request.GET.get('id', 0)) != 0
    edit_info = {
        'edit_mode':  edit_mode_valid,
        'pd_id': int(request.GET.get('id', 0))
    }

    if edit_mode_valid:
        pd = ProductInventory.objects.select_related(
            'product', 'product_type', 'brand'
        ).prefetch_related(
            'media_product_inventory'
        ).get(pk=edit_info['pd_id'])
        edit_info['product_info'] = pd
    print(edit_info)

    if request.method == 'POST':
        pass
    context = {
        'cate':categories_p,
        'products':product,
        'brands':brand,
        'product_type':product_type,
        'product_inv':product_inventory,
        'edit_info': edit_info
    }
    return render(request, "dashboard/add_product.html",context)


def store_product_data():
    """
    This stores data of products in database to be used on the home pages
    :return:
    """
    pass


def product_csv_reader():
    """
    This reads data from a csv file of the products
    :return:
    """
    pass


def product_csv_writer():
    """
    This writes data to a csv file of the products
    :return:
    """
    pass


def product_data_collector(request):
    if request.method == "POST":
        web_id = request.POST.get('website_id')
        safe_url = request.POST.get('safe_url')
        is_active = request.POST.get('is_active') == 'true'
        description = request.POST.get('description')
        category = request.POST.get('category')
        product_name = request.POST.get('product_name')

        print('visibity',is_active)
        is_active = is_active == 'true'

        new_product = Product(
            web_id=web_id,
            slug=safe_url,
            name=product_name,
            description=description,
            is_active=is_active
        )
        new_product.save()
        new_product.category.add(category)

        return redirect('add')

    return redirect('add')

def inventory_data_collector(request):
    if request.method == "POST":
        try:
            # Get form data
            sku = request.POST.get('sku')
            upc = request.POST.get('upc')
            product_type_id = request.POST.get('product_type')
            product_id = request.POST.get('product')
            brand_id = request.POST.get('brand')
            weight = request.POST.get('weight')
            retail_price = request.POST.get('msrp')
            regular_price = request.POST.get('regular_price')
            sale_price = request.POST.get('sale_price')
            is_active = request.POST.get('is_active') == 'true'

            try:
                product_type = ProductType.objects.get(pk=product_type_id)
                product = Product.objects.get(pk=product_id)
                brand = Brand.objects.get(pk=brand_id)
            except ObjectDoesNotExist:
                return redirect('add')

            new_inventory_details = ProductInventory(
                sku=sku,
                upc=upc,
                product_type=product_type,  
                product=product,           
                brand=brand,                
                weight=weight,
                sale_price=sale_price,
                store_price=regular_price,
                retail_price=retail_price,
                is_active=is_active,
            )
            new_inventory_details.save()
            
            
        except Exception as e:
            print(f"Error creating inventory: {str(e)}")
            
    return redirect('add')


def media_collection(request):
    if request.method == "POST":
        product_id = request.POST.get('product_inv')
        alt_text = request.POST.get('main_image_alt')
        image = request.FILES.get('main_image')
        is_feature = request.POST.get("is_feature") == "true"
        print('outputted this img ', image)

        product = get_object_or_404(ProductInventory, pk=product_id)
        print("let she this bullshit tooo:",request.FILES)

        new_image = Media(
            product_inventory=product,
            image=image,  # Save the uploaded image
            alt_text=alt_text,
            is_feature = is_feature,
        )
        new_image.save()

        return redirect('add')  

    return redirect('add')


