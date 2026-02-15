from django.shortcuts import render, redirect
from django.http import HttpResponse
from httpx import request
from .forms import ProductForm
from .models import Product
from django.shortcuts import get_object_or_404, redirect
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




