from django.contrib import admin
from .models import Restaurant, Table


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'address', 'phone', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'owner__username', 'address', 'phone')
    date_hierarchy = 'created_at'


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant', 'seats', 'is_active', 'created_at')
    list_filter = ('is_active', 'restaurant')
    search_fields = ('name', 'restaurant__name')
    readonly_fields = ('qr_code', 'uuid') 