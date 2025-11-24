from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm
from .models import Aplicacion, ContactMessage, AvailableSlot
from datetime import datetime

# Formulario de registro con selección de tipo de usuario
class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    USER_TYPE_CHOICES = [
        ('vip', 'Usuario VIP (Solicitar citas)'),
    ]
    user_type = forms.ChoiceField(
        choices=USER_TYPE_CHOICES,
        widget=forms.RadioSelect,
        initial='vip',
        label='Tipo de cuenta'
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Asignar al grupo VIP automáticamente
            vip_group, created = Group.objects.get_or_create(name='VIP')
            user.groups.add(vip_group)
        return user

# Formulario de contacto
class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "subject", "message"]
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5}),
        }

# Formulario para que VIPs soliciten citas
class AplicacionForm(forms.ModelForm):
    class Meta:
        model = Aplicacion
        fields = ["title", "date", "time", "notes"]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'min': datetime.now().date()}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Motivo de la cita o detalles adicionales'}),
        }
        labels = {
            'title': 'Título de la cita',
            'date': 'Fecha',
            'time': 'Hora',
            'notes': 'Notas',
        }

# Formulario para que trabajadores gestionen citas
class AplicacionManageForm(forms.ModelForm):
    class Meta:
        model = Aplicacion
        fields = ["status", "admin_notes"]
        widgets = {
            'admin_notes': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'status': 'Estado',
            'admin_notes': 'Notas internas',
        }

# Formulario para configurar horarios disponibles
class AvailableSlotForm(forms.ModelForm):
    class Meta:
        model = AvailableSlot
        fields = ["day_of_week", "start_time", "end_time", "max_appointments", "is_active"]
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }
        labels = {
            'day_of_week': 'Día de la semana',
            'start_time': 'Hora inicio',
            'end_time': 'Hora fin',
            'max_appointments': 'Máximo de citas',
            'is_active': 'Activo',
        }