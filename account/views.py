from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
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


def hash_password(raw_password):
    return hashlib.sha256(raw_password.encode()).hexdigest()


def check_password(raw_password, hashed):
    return hash_password(raw_password) == hashed



def register(request):
    """Registro público — siempre crea un usuario con rol 'cliente'."""
    if request.session.get('user_id'):
        return redirect('home')

    if request.method == 'POST':
        first_name  = request.POST.get('first_name', '').strip()
        last_name   = request.POST.get('last_name', '').strip()
        email       = request.POST.get('email', '').strip().lower()
        password    = request.POST.get('password', '')
        password2   = request.POST.get('password2', '')
        phone       = request.POST.get('phone', '').strip()
        address     = request.POST.get('address', '').strip()
        city        = request.POST.get('city', '').strip()

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

        request.session['user_id'] = user.id
        request.session['user_role'] = user.role
        request.session['user_name'] = user.first_name

        messages.success(request, f'¡Bienvenida, {user.first_name}! Tu cuenta fue creada.')
        return redirect('home')

    return render(request, 'account/register.html', {'post': {}})



def login_view(request):
    """Login para todos los roles. Redirige según el rol detectado."""
    if request.session.get('user_id'):
        return _redirect_by_role(request.session.get('user_role'))

    if request.method == 'POST':
        email    = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'Correo o contraseña incorrectos.')
            return render(request, 'account/login.html', {'email': email})

        if not check_password(password, user.password):
            messages.error(request, 'Correo o contraseña incorrectos.')
            return render(request, 'account/login.html', {'email': email})

        request.session['user_id']   = user.id
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
    else:
        return redirect('home')


def logout_view(request):
    request.session.flush()
    messages.success(request, 'Sesión cerrada correctamente.')
    return redirect('login')