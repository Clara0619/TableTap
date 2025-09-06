from django.db import models
from restaurant.models import Restaurant


class Menu(models.Model):
    """
    Menu model that belongs to a restaurant
    """
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menus')
    name = models.CharField('Menu Name', max_length=100)
    description = models.TextField('Menu Description', blank=True)
    is_active = models.BooleanField('Active Status', default=True)
    created_at = models.DateTimeField('Created Time', auto_now_add=True)
    updated_at = models.DateTimeField('Updated Time', auto_now=True)
    
    class Meta:
        verbose_name = 'Menu'
        verbose_name_plural = 'Menus'
        
    def __str__(self):
        return f"{self.restaurant.name} - {self.name}"


class Category(models.Model):
    """
    Category model for menu items
    """
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField('Category Name', max_length=100)
    description = models.TextField('Category Description', blank=True)
    order = models.PositiveSmallIntegerField('Order', default=0)
    is_active = models.BooleanField('Active Status', default=True)
    
    class Meta:
        verbose_name = 'Menu Category'
        verbose_name_plural = 'Menu Categories'
        ordering = ['order', 'id']
        
    def __str__(self):
        return self.name


class MenuItem(models.Model):
    """
    Menu item model
    """
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')
    name = models.CharField('Item Name', max_length=100)
    description = models.TextField('Item Description', blank=True)
    price = models.DecimalField('Price', max_digits=10, decimal_places=2)
    image = models.ImageField('Item Image', upload_to='menu_items/', blank=True, null=True)
    is_available = models.BooleanField('Available', default=True)
    is_featured = models.BooleanField('Featured', default=False)
    order = models.PositiveSmallIntegerField('Order', default=0)
    created_at = models.DateTimeField('Created Time', auto_now_add=True)
    updated_at = models.DateTimeField('Updated Time', auto_now=True)
    
    class Meta:
        verbose_name = 'Menu Item'
        verbose_name_plural = 'Menu Items'
        ordering = ['order', 'id']
        
    def __str__(self):
        return self.name