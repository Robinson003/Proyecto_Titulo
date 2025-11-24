from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

# Modelo de Citas mejorado con estados y aprobación
class Aplicacion(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('confirmed', 'Confirmada'),
        ('cancelled', 'Cancelada'),
        ('completed', 'Completada'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='citas')
    title = models.CharField(max_length=200, default="Cita")
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, verbose_name="Notas del cliente")
    
    # Campos de gestión
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='citas_aprobadas')
    admin_notes = models.TextField(blank=True, verbose_name="Notas internas")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date', 'time']
        verbose_name = 'Cita'
        verbose_name_plural = 'Citas'

    def __str__(self):
        return f"{self.user.username} - {self.date} {self.time} ({self.get_status_display()})"
    
    def clean(self):
        # Validar que no haya otra cita en el mismo horario
        if self.date and self.time:
            conflicting = Aplicacion.objects.filter(
                date=self.date,
                time=self.time,
                status__in=['pending', 'confirmed']
            ).exclude(pk=self.pk)
            
            if conflicting.exists():
                raise ValidationError('Ya existe una cita en este horario.')

# Horarios disponibles configurables por los trabajadores
class AvailableSlot(models.Model):
    DAYS_OF_WEEK = [
        (0, 'Lunes'),
        (1, 'Martes'),
        (2, 'Miércoles'),
        (3, 'Jueves'),
        (4, 'Viernes'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ]
    
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    max_appointments = models.IntegerField(default=1, help_text="Máximo de citas por slot")
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['day_of_week', 'start_time']
        verbose_name = 'Horario Disponible'
        verbose_name_plural = 'Horarios Disponibles'
    
    def __str__(self):
        return f"{self.get_day_of_week_display()} {self.start_time} - {self.end_time}"

# Modelo de Contacto (sin cambios, pero agregamos más info)
class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=150, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Mensaje de Contacto'
        verbose_name_plural = 'Mensajes de Contacto'

    def __str__(self):
        return f"{self.name} - {self.email}"