from django.db import models
from django.conf import settings
from restaurant.models import Restaurant, Table
from menu.models import MenuItem


class Order(models.Model):
    """
    Order model for customer orders
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('preparing', 'Preparing'),
        ('served', 'Served'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='orders')
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, related_name='orders')
    
    status = models.CharField('Order Status', max_length=20, choices=STATUS_CHOICES, default='pending')
    special_instructions = models.TextField('Special Instructions', blank=True)
    
    total_price = models.DecimalField('Total Price', max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField('Created At', auto_now_add=True)
    updated_at = models.DateTimeField('Updated At', auto_now=True)
    
    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Order #{self.id} - {self.restaurant.name} - {self.status}"
    
    def calculate_total(self):
        """Calculate total price of the order"""
        total = sum(item.subtotal for item in self.items.all())
        self.total_price = total
        self.save()
        return total


class OrderItem(models.Model):
    """
    Order item model for items in an order
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField('Quantity', default=1)
    unit_price = models.DecimalField('Unit Price', max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
        
    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name}"
        
    @property
    def subtotal(self):
        """Calculate subtotal for this item"""
        return self.quantity * self.unit_price
        
    def save(self, *args, **kwargs):
        # Set unit price if not already set
        if not self.unit_price:
            self.unit_price = self.menu_item.price
        super().save(*args, **kwargs)
        
        # Update order total
        self.order.calculate_total()


class Cart(models.Model):
    """
    Shopping cart model for storing items before checkout
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='carts')
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, related_name='carts')
    created_at = models.DateTimeField('Created At', auto_now_add=True)
    updated_at = models.DateTimeField('Updated At', auto_now=True)
    
    class Meta:
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'
        
    def __str__(self):
        return f"{self.user.username}'s Cart"
    
    @property
    def total(self):
        """Calculate total price of the cart"""
        return sum(item.subtotal for item in self.items.all())
        
    def clear(self):
        """Remove all items from cart"""
        self.items.all().delete()


class CartItem(models.Model):
    """
    Cart item model for items in the shopping cart
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField('Quantity', default=1)
    
    class Meta:
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        
    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name}"
        
    @property
    def subtotal(self):
        """Calculate subtotal for this item"""
        return self.quantity * self.menu_item.price 