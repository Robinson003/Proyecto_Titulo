from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import CalendarView

urlpatterns = [
    # ============================================
    # RUTAS PÚBLICAS
    # ============================================
    path("", views.home, name="home"),
    path("register/", views.register_view, name="register"),
    path("login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("contact/", views.contact_view, name="contact"),
    
    # ============================================
    # RUTAS PARA USUARIOS VIP
    # ============================================
    path("vip/dashboard/", views.vip_dashboard, name="vip_dashboard"),
    path("vip/request/", views.request_appointment, name="request_appointment"),
    path("vip/my-appointments/", views.my_appointments, name="my_appointments"),
    path("vip/cancel/<int:pk>/", views.cancel_appointment, name="cancel_appointment"),
    
    # Calendario VIP
    path("vip/calendar/", CalendarView.as_view(), name="calendar"),
    path("vip/api/events/", views.my_events, name="api_events"),
    path("vip/api/events/create/", views.create_event, name="api_create_event"),
    path("vip/api/events/delete/<int:pk>/", views.delete_event, name="api_delete_event"),
    
    # ============================================
    # RUTAS PARA TRABAJADORES
    # ============================================
    path("worker/dashboard/", views.worker_dashboard, name="worker_dashboard"),
    path("worker/appointments/", views.manage_appointments, name="manage_appointments"),
    path("worker/appointments/approve/<int:pk>/", views.approve_appointment, name="approve_appointment"),
    path("worker/slots/", views.manage_slots, name="manage_slots"),
    path("worker/slots/delete/<int:pk>/", views.delete_slot, name="delete_slot"),
    path("worker/messages/", views.view_messages, name="view_messages"),
    path("worker/messages/read/<int:pk>/", views.mark_message_read, name="mark_message_read"),
    
    # ============================================
    # RUTAS DE PERFIL (TODOS LOS USUARIOS AUTENTICADOS)
    # ============================================
    path("profile/", views.profile, name="profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
]