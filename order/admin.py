from django.contrib import admin
from .models import Order, OrderItem, Cart, CartItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('menu_item', 'quantity', 'unit_price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'restaurant', 'customer', 'status', 'total_price', 'created_at')
    list_filter = ('status', 'restaurant', 'created_at')
    search_fields = ('id', 'customer__username', 'restaurant__name')
    readonly_fields = ('total_price',)
    inlines = [OrderItemInline]
    date_hierarchy = 'created_at'


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'restaurant', 'total', 'created_at')
    list_filter = ('restaurant', 'created_at')
    search_fields = ('user__username', 'restaurant__name')
    inlines = [CartItemInline]
    date_hierarchy = 'created_at' 