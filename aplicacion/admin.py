from django.contrib import admin
from .models import Aplicacion, ContactMessage, AvailableSlot

@admin.register(Aplicacion)
class AplicacionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'title', 'date', 'time', 'status', 'created_at']
    list_filter = ['status', 'date', 'created_at']
    search_fields = ['user__username', 'user__email', 'title', 'notes']
    list_editable = ['status']
    date_hierarchy = 'date'
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información básica', {
            'fields': ('user', 'title', 'date', 'time', 'status')
        }),
        ('Detalles', {
            'fields': ('notes', 'admin_notes', 'approved_by')
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email', 'subject', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    list_editable = ['is_read']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'

@admin.register(AvailableSlot)
class AvailableSlotAdmin(admin.ModelAdmin):
    list_display = ['id', 'day_of_week', 'start_time', 'end_time', 'max_appointments', 'is_active', 'created_by']
    list_filter = ['day_of_week', 'is_active', 'created_by']
    list_editable = ['is_active']
    readonly_fields = ['created_at']