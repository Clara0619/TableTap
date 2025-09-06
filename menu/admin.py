from django.contrib import admin
from .models import Menu, Category, MenuItem


class CategoryInline(admin.TabularInline):
    model = Category
    extra = 1


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant', 'is_active', 'created_at')
    list_filter = ('is_active', 'restaurant')
    search_fields = ('name', 'restaurant__name')
    inlines = [CategoryInline]


class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'menu', 'order', 'is_active')
    list_filter = ('is_active', 'menu')
    search_fields = ('name', 'menu__name')
    inlines = [MenuItemInline]


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_available', 'is_featured', 'order')
    list_filter = ('is_available', 'is_featured', 'category')
    search_fields = ('name', 'category__name')
    list_editable = ('price', 'is_available', 'is_featured', 'order') 