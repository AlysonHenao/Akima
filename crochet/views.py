from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from .forms import ProductForm
from .models import Product, Cart, CartItem
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
import json
# Create your views here.
def home(request):
    products = Product.objects.filter(is_active=True)
    return render(request, 'home.html', {
        'products': products
    })

def owner(request):
    products = Product.objects.all()

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('owner')

    else:
        form = ProductForm()

    return render(request, 'owner.html', {
        'form': form,
        'products': products
    })

def employee(request):
    return HttpResponse('<h1>Employee</h1>')


def toggle_product_status(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.is_active = not product.is_active
    product.save()
    return redirect('owner')

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    available_sizes = [size.strip() for size in product.available_sizes.split(',')]
    available_colors = [color.strip() for color in product.available_colors.split(',')]
    
    return render(request, 'product_detail.html', {
        'product': product,
        'available_sizes': available_sizes,
        'available_colors': available_colors
    })


def get_or_create_cart(request):
    if not request.session.session_key:
        request.session.create()
    
    session_key = request.session.session_key
    cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart


@require_POST
def add_to_cart(request):
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        size = data.get('size')
        color = data.get('color')
        quantity = data.get('quantity', 1)

        product = get_object_or_404(Product, id=product_id)
        cart = get_or_create_cart(request)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            size=size,
            color=color,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return JsonResponse({
            'success': True,
            'message': 'Product added to cart!',
            'cart_count': cart.get_item_count()
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


def view_cart(request):
    cart = get_or_create_cart(request)
    return render(request, 'cart.html', {
        'cart': cart
    })


@require_POST
def update_cart_item(request, item_id):
    try:
        data = json.loads(request.body)
        quantity = data.get('quantity')
        
        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()
            
        return JsonResponse({
            'success': True,
            'cart_total': float(cart.get_total()),
            'cart_count': cart.get_item_count()
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


def remove_from_cart(request, item_id):
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    cart_item.delete()
    return redirect('view_cart')





