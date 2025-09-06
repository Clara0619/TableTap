import uuid
import qrcode
from io import BytesIO
from django.db import models
from django.conf import settings
from django.core.files.base import ContentFile
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from PIL import Image


class Restaurant(models.Model):
    """
    Restaurant model for restaurant owners
    """
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='restaurants')
    name = models.CharField('Restaurant Name', max_length=100)
    description = models.TextField('Description', blank=True)
    address = models.CharField('Address', max_length=200)
    phone = models.CharField('Contact Phone', max_length=15)
    logo = models.ImageField('Restaurant Logo', upload_to='restaurant_logos/', blank=True, null=True)
    is_active = models.BooleanField('Active Status', default=True)
    created_at = models.DateTimeField('Created At', auto_now_add=True)
    updated_at = models.DateTimeField('Updated At', auto_now=True)
    
    class Meta:
        verbose_name = 'Restaurant'
        verbose_name_plural = 'Restaurants'
        
    def __str__(self):
        return self.name


class Table(models.Model):
    """
    Table model for each restaurant
    """
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='tables')
    name = models.CharField('Table Name/Number', max_length=50)
    seats = models.PositiveSmallIntegerField('Number of Seats', default=4)
    qr_code = models.ImageField('QR Code', upload_to='table_qrcodes/', blank=True, null=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    is_active = models.BooleanField('Active Status', default=True)
    created_at = models.DateTimeField('Created At', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Table'
        verbose_name_plural = 'Tables'
        
    def __str__(self):
        return f"{self.restaurant.name} - {self.name}"
    
    def save(self, *args, **kwargs):
        # Generate QR code when saving a table
        if not self.qr_code:
            self.generate_qr_code()
        super().save(*args, **kwargs)
    
    def get_menu_url(self):
        
        if settings.DEBUG:
            base_url = 'https://infs3202-c47c18f0.uqcloud.net/'
        else:
            
            base_url = 'https://tabletap.example.com'
            
        
        path = reverse('menu:menu_view', kwargs={'table_uuid': self.uuid})
        return f"{base_url}{path}"
    
    
    @property
    def menu_url(self):
        return self.get_menu_url()
    
    def generate_qr_code(self):
    #"""Generate QR code image for this table"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
    
    
        url = self.get_menu_url()
        qr.add_data(url)
        qr.make(fit=True)
    
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
    
        
        filename = f"table_qr_{self.uuid}.png"
    
       
        import os
        media_path = os.path.join(settings.MEDIA_ROOT, 'table_qrcodes')
        if not os.path.exists(media_path):
            os.makedirs(media_path, exist_ok=True)
    
        self.qr_code.save(filename, ContentFile(buffer.getvalue()), save=False)
    
        
        print(f"QR code saved as: {self.qr_code.path}")
        buffer.close()