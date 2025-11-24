from .forms import RegisterForm, ContactForm, AplicacionForm, AplicacionManageForm, AvailableSlotForm
from .models import Aplicacion, AvailableSlot, ContactMessage
from .decorators import vip_required, worker_required
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView
from datetime import datetime, timedelta

# ============================================
# VISTAS PÚBLICAS (sin autenticación)
# ============================================

def home(request):
    """Página principal - accesible para todos"""
    return render(request, "home.html")

def register_view(request):
    """Registro de usuarios VIP"""
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"¡Bienvenido {user.username}! Tu cuenta VIP ha sido creada.")
            return redirect("vip_dashboard")
    else:
        form = RegisterForm()
    return render(request, "register.html", {"form": form})

def contact_view(request):
    """Formulario de contacto público"""
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "¡Mensaje enviado! Te contactaremos pronto.")
            return redirect("contact")
    else:
        form = ContactForm()
    return render(request, "contact.html", {"form": form})

def logout_view(request):
    """Cerrar sesión"""
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect("home")

# ============================================
# VISTAS PARA USUARIOS VIP
# ============================================

@vip_required
def vip_dashboard(request):
    """Dashboard principal para usuarios VIP"""
    user_citas = Aplicacion.objects.filter(user=request.user)
    
    # Estadísticas
    pending_count = user_citas.filter(status='pending').count()
    confirmed_count = user_citas.filter(status='confirmed').count()
    
    # Próximas citas
    upcoming = user_citas.filter(
        date__gte=timezone.now().date(),
        status__in=['pending', 'confirmed']
    ).order_by('date', 'time')[:5]
    
    # Historial (últimas 10)
    history = user_citas.filter(
        Q(date__lt=timezone.now().date()) | Q(status__in=['cancelled', 'completed'])
    ).order_by('-date', '-time')[:10]
    
    context = {
        'pending_count': pending_count,
        'confirmed_count': confirmed_count,
        'upcoming': upcoming,
        'history': history,
    }
    return render(request, "vip/dashboard.html", context)

@vip_required
def request_appointment(request):
    """Solicitar nueva cita"""
    if request.method == "POST":
        form = AplicacionForm(request.POST)
        if form.is_valid():
            cita = form.save(commit=False)
            cita.user = request.user
            cita.status = 'pending'
            try:
                cita.full_clean()  # Valida que no haya conflictos
                cita.save()
                messages.success(request, "¡Cita solicitada! Espera confirmación de nuestro equipo.")
                return redirect("vip_dashboard")
            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
    else:
        form = AplicacionForm()
    
    # Mostrar horarios disponibles
    slots = AvailableSlot.objects.filter(is_active=True).order_by('day_of_week', 'start_time')
    
    context = {
        'form': form,
        'slots': slots,
    }
    return render(request, "vip/request_appointment.html", context)

@vip_required
def my_appointments(request):
    """Lista completa de citas del usuario"""
    citas = Aplicacion.objects.filter(user=request.user).order_by('-date', '-time')
    
    # Filtros
    status_filter = request.GET.get('status', '')
    if status_filter:
        citas = citas.filter(status=status_filter)
    
    context = {
        'citas': citas,
        'status_filter': status_filter,
    }
    return render(request, "vip/my_appointments.html", context)

@vip_required
def cancel_appointment(request, pk):
    """Cancelar una cita propia"""
    cita = get_object_or_404(Aplicacion, pk=pk, user=request.user)
    
    if cita.status in ['pending', 'confirmed']:
        cita.status = 'cancelled'
        cita.save()
        messages.success(request, "Cita cancelada correctamente.")
    else:
        messages.warning(request, "No se puede cancelar esta cita.")
    
    return redirect("my_appointments")

# ============================================
# VISTAS PARA TRABAJADORES
# ============================================

@worker_required
def worker_dashboard(request):
    """Dashboard principal para trabajadores"""
    today = timezone.now().date()
    
    # Estadísticas generales
    total_pending = Aplicacion.objects.filter(status='pending').count()
    total_confirmed = Aplicacion.objects.filter(status='confirmed').count()
    total_users = User.objects.filter(groups__name='VIP').count()
    
    # Citas de hoy
    today_appointments = Aplicacion.objects.filter(date=today).order_by('time')
    
    # Citas pendientes de aprobación
    pending_appointments = Aplicacion.objects.filter(status='pending').order_by('date', 'time')[:10]
    
    # Próximas citas confirmadas
    upcoming_confirmed = Aplicacion.objects.filter(
        status='confirmed',
        date__gte=today
    ).order_by('date', 'time')[:10]
    
    context = {
        'total_pending': total_pending,
        'total_confirmed': total_confirmed,
        'total_users': total_users,
        'today_appointments': today_appointments,
        'pending_appointments': pending_appointments,
        'upcoming_confirmed': upcoming_confirmed,
    }
    return render(request, "worker/dashboard.html", context)

@worker_required
def manage_appointments(request):
    """Gestión completa de citas"""
    citas = Aplicacion.objects.select_related('user').order_by('-date', '-time')
    
    # Filtros
    status = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    user_search = request.GET.get('user', '')
    
    if status:
        citas = citas.filter(status=status)
    if date_from:
        citas = citas.filter(date__gte=date_from)
    if date_to:
        citas = citas.filter(date__lte=date_to)
    if user_search:
        citas = citas.filter(
            Q(user__username__icontains=user_search) |
            Q(user__email__icontains=user_search)
        )
    
    context = {
        'citas': citas,
        'status_filter': status,
        'date_from': date_from,
        'date_to': date_to,
        'user_search': user_search,
    }
    return render(request, "worker/manage_appointments.html", context)

@worker_required
def approve_appointment(request, pk):
    """Aprobar/Rechazar cita"""
    cita = get_object_or_404(Aplicacion, pk=pk)
    
    if request.method == "POST":
        form = AplicacionManageForm(request.POST, instance=cita)
        if form.is_valid():
            cita = form.save(commit=False)
            cita.approved_by = request.user
            cita.save()
            
            status_text = cita.get_status_display()
            messages.success(request, f"Cita actualizada a: {status_text}")
            return redirect("manage_appointments")
    else:
        form = AplicacionManageForm(instance=cita)
    
    context = {
        'form': form,
        'cita': cita,
    }
    return render(request, "worker/approve_appointment.html", context)

@worker_required
def manage_slots(request):
    """Gestión de horarios disponibles"""
    slots = AvailableSlot.objects.filter(created_by=request.user).order_by('day_of_week', 'start_time')
    
    if request.method == "POST":
        form = AvailableSlotForm(request.POST)
        if form.is_valid():
            slot = form.save(commit=False)
            slot.created_by = request.user
            slot.save()
            messages.success(request, "Horario agregado correctamente.")
            return redirect("manage_slots")
    else:
        form = AvailableSlotForm()
    
    context = {
        'form': form,
        'slots': slots,
    }
    return render(request, "worker/manage_slots.html", context)

@worker_required
def delete_slot(request, pk):
    """Eliminar horario disponible"""
    slot = get_object_or_404(AvailableSlot, pk=pk, created_by=request.user)
    slot.delete()
    messages.success(request, "Horario eliminado.")
    return redirect("manage_slots")

@worker_required
def view_messages(request):
    """Ver mensajes de contacto"""
    messages_list = ContactMessage.objects.order_by('-created_at')
    
    context = {
        'messages_list': messages_list,
    }
    return render(request, "worker/view_messages.html", context)

@worker_required
def mark_message_read(request, pk):
    """Marcar mensaje como leído"""
    message = get_object_or_404(ContactMessage, pk=pk)
    message.is_read = True
    message.save()
    return redirect("view_messages")

# ============================================
# VISTAS DE PERFIL (TODOS LOS USUARIOS)
# ============================================

@login_required
def profile(request):
    """Perfil básico del usuario"""
    user_groups = request.user.groups.values_list('name', flat=True)
    
    context = {
        'user_groups': list(user_groups),
    }
    return render(request, "profile.html", context)

@login_required
def edit_profile(request):
    """Editar información del perfil"""
    if request.method == "POST":
        user = request.user
        user.first_name = request.POST.get("first_name", "")
        user.last_name = request.POST.get("last_name", "")
        user.email = request.POST.get("email", "")
        user.save()
        messages.success(request, "Perfil actualizado correctamente ✅")
        return redirect("profile")
    return render(request, "edit_profile.html")

# ============================================
# API ENDPOINTS PARA CALENDARIO (VIP)
# ============================================

@vip_required
def my_events(request):
    """API: Eventos del usuario para FullCalendar"""
    appts = Aplicacion.objects.filter(user=request.user)
    events = []
    for a in appts:
        # Color según estado
        color_map = {
            'pending': '#FFA500',
            'confirmed': '#28A745',
            'cancelled': '#DC3545',
            'completed': '#6C757D',
        }
        
        events.append({
            "id": a.id,
            "title": f"{a.title} ({a.get_status_display()})",
            "start": f"{a.date}T{a.time}",
            "allDay": False,
            "backgroundColor": color_map.get(a.status, '#007BFF'),
        })
    return JsonResponse(events, safe=False)

@vip_required
@require_http_methods(["POST"])
def create_event(request):
    """API: Crear evento"""
    form = AplicacionForm(request.POST)
    if form.is_valid():
        ap = form.save(commit=False)
        ap.user = request.user
        ap.status = 'pending'
        try:
            ap.full_clean()
            ap.save()
            return JsonResponse({"status": "ok", "id": ap.id})
        except Exception as e:
            return JsonResponse({"status": "error", "errors": str(e)}, status=400)
    return JsonResponse({"status": "error", "errors": form.errors}, status=400)

@vip_required
@require_http_methods(["POST"])
def delete_event(request, pk):
    """API: Eliminar evento"""
    ap = get_object_or_404(Aplicacion, pk=pk, user=request.user)
    ap.delete()
    return JsonResponse({"status": "deleted"})

# ============================================
# CALENDARIO VIEW (VIP)
# ============================================

@method_decorator(vip_required, name='dispatch')
class CalendarView(TemplateView):
    template_name = "calendar.html"