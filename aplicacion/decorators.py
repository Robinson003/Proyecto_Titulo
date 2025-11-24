from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from functools import wraps

# Verifica si el usuario es VIP
def is_vip(user):
    return user.groups.filter(name='VIP').exists()

# Verifica si el usuario es Trabajador
def is_worker(user):
    return user.groups.filter(name='Trabajadores').exists() or user.is_staff

# Decorador para vistas que requieren VIP
def vip_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not is_vip(request.user):
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper

# Decorador para vistas que requieren Trabajador
def worker_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not is_worker(request.user):
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper