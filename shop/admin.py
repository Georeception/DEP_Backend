from django.contrib import admin
from .models import PickupLocation

@admin.register(PickupLocation)
class PickupLocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'state', 'phone', 'email', 'is_active')
    list_filter = ('is_active', 'city', 'state')
    search_fields = ('name', 'address', 'city', 'state', 'phone', 'email')
    ordering = ('city', 'name')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'is_active')
        }),
        ('Location Details', {
            'fields': ('address', 'city', 'state', 'zip_code')
        }),
        ('Contact Information', {
            'fields': ('phone', 'email')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    ) 