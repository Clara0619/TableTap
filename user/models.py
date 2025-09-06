from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Custom User model for TableTap
    """
    USER_TYPE_CHOICES = (
        ('customer', 'Customer'),
        ('restaurant', 'Restaurant Owner'),
        ('admin', 'Administrator'),
    )
    
    user_type = models.CharField('User Type', max_length=10, choices=USER_TYPE_CHOICES, default='customer')
    phone = models.CharField('Phone Number', max_length=15, blank=True)
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        
    def __str__(self):
        return self.username
        
    @property
    def is_customer(self):
        return self.user_type == 'customer'
        
    @property
    def is_restaurant_owner(self):
        return self.user_type == 'restaurant' 