from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.core.mail import send_mail
from functools import wraps
import hashlib
from .models import User


def require_login(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            messages.error(request, 'Debes iniciar sesión para acceder a esta página.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


def require_role(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.session.get('user_id'):
                messages.error(request, 'Debes iniciar sesión para acceder a esta página.')
                return redirect('login')

            user_role = request.session.get('user_role')
            if user_role not in allowed_roles:
                messages.error(request, 'No tienes permiso para acceder a esta página.')
                return redirect('login')

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# ======================
# UTILIDADES
# ======================

def hash_password(raw_password):
    return hashlib.sha256(raw_password.encode()).hexdigest()


def check_password(raw_password, hashed):
    return hash_password(raw_password) == hashed




@require_login
def profile_view(request):
    user = User.objects.get(id=request.session.get('user_id'))
    return render(request, 'account/profile.html', {'user': user})


@require_login
def edit_profile(request):
    user = User.objects.get(id=request.session.get('user_id'))

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', '').strip()
        user.last_name  = request.POST.get('last_name', '').strip()
        user.email      = request.POST.get('email', '').strip().lower()
        user.phone      = request.POST.get('phone', '').strip()
        user.address    = request.POST.get('address', '').strip()
        user.city       = request.POST.get('city', '').strip()

        user.save()
        request.session['user_name'] = user.first_name

        messages.success(request, 'Perfil actualizado correctamente.')
        return redirect('profile')

    return render(request, 'account/edit_profile.html', {'user': user})



@require_role('administrador')
def manage_users(request):
    from production.models import EmployeeInventory, ProductionTask
    from order.models import Order

    search = request.GET.get('search', '').strip()
    role = request.GET.get('role', '').strip()
    selected_user_id = request.GET.get('user_id')

    users = User.objects.all().order_by('first_name', 'last_name')

    if search:
        users = users.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search)
        )

    if role:
        users = users.filter(role=role)

    paginator = Paginator(users, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    selected_user = None
    inventory = []
    assigned_tasks = []
    customer_orders = []

    if selected_user_id:
        selected_user = get_object_or_404(User, id=selected_user_id)

        inventory = EmployeeInventory.objects.filter(
            employee=selected_user
        ).select_related('supply')

        assigned_tasks = ProductionTask.objects.filter(
            employee=selected_user
        ).select_related(
            'product__product',
            'product__general_color',
            'order_detail__order__user'
        ).order_by('-assignment_date')

        customer_orders = Order.objects.filter(
            user=selected_user
        ).prefetch_related(
            'details__product',
            'details__color_product__general_color'
        ).order_by('-order_date')

    return render(request, 'account/manage_users.html', {
        'users': page_obj,
        'page_obj': page_obj,
        'roles': User.ROLES,
        'search': search,
        'role': role,
        'selected_user': selected_user,
        'inventory': inventory,
        'assigned_tasks': assigned_tasks,
        'customer_orders': customer_orders,
    })


@require_role('administrador')
def update_user_role(request, user_id):
    user = get_object_or_404(User, id=user_id)
    new_role = request.POST.get('role')

    valid_roles = [role[0] for role in User.ROLES]

    if new_role not in valid_roles:
        messages.error(request, 'Rol no válido.')
        return redirect('manage_users')

    if user.id == request.session.get('user_id') and new_role != 'administrador':
        messages.error(request, 'No puedes cambiar tu propio rol.')
        return redirect('manage_users')

    user.role = new_role
    user.save()

    messages.success(request, f'Rol actualizado para {user.first_name}.')
    return redirect('manage_users')


def register(request):
    if request.session.get('user_id'):
        return redirect('home')

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name  = request.POST.get('last_name', '').strip()
        email      = request.POST.get('email', '').strip().lower()
        password   = request.POST.get('password', '')
        password2  = request.POST.get('password2', '')
        phone      = request.POST.get('phone', '').strip()
        address    = request.POST.get('address', '').strip()
        city       = request.POST.get('city', '').strip()

        if not all([first_name, last_name, email, password, phone, address, city]):
            messages.error(request, 'Por favor completa todos los campos.')
            return render(request, 'account/register.html', {'post': request.POST})

        if password != password2:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'account/register.html', {'post': request.POST})

        if len(password) < 6:
            messages.error(request, 'La contraseña debe tener al menos 6 caracteres.')
            return render(request, 'account/register.html', {'post': request.POST})

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Ya existe una cuenta con ese correo.')
            return render(request, 'account/register.html', {'post': request.POST})

        user = User.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=hash_password(password),
            role='cliente',
            phone=phone,
            address=address,
            city=city,
        )

        send_mail(
            subject='Bienvenida a Akima',
            message=f'Hola {user.first_name}, tu cuenta fue creada.',
            from_email=None,
            recipient_list=[user.email],
            fail_silently=True,
        )

        request.session['user_id'] = user.id
        request.session['user_role'] = user.role
        request.session['user_name'] = user.first_name

        messages.success(request, f'¡Bienvenida, {user.first_name}!')
        return redirect('home')

    return render(request, 'account/register.html', {'post': {}})


def login_view(request):
    if request.session.get('user_id'):
        return _redirect_by_role(request.session.get('user_role'))

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'Correo o contraseña incorrectos.')
            return render(request, 'account/login.html', {'email': email})

        if not check_password(password, user.password):
            messages.error(request, 'Correo o contraseña incorrectos.')
            return render(request, 'account/login.html', {'email': email})

        request.session['user_id'] = user.id
        request.session['user_role'] = user.role
        request.session['user_name'] = user.first_name

        messages.success(request, f'¡Bienvenida, {user.first_name}!')
        return _redirect_by_role(user.role)

    return render(request, 'account/login.html', {'email': ''})


def _redirect_by_role(role):
    if role == 'administrador':
        return redirect('administrator')
    elif role == 'empleada':
        return redirect('employee')
    return redirect('home')


def logout_view(request):
    request.session.flush()
    messages.success(request, 'Sesión cerrada correctamente.')
    return redirect('login')