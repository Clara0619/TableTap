from django.urls import path
from . import views

app_name = 'order'

urlpatterns = [
    # Cart views
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart_no_table'),
    path('cart/<uuid:table_uuid>/', views.view_cart, name='view_cart'),
    path('cart/update/', views.update_cart, name='update_cart'),
    path('cart/remove/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/<uuid:table_uuid>/', views.checkout, name='checkout'),
    
    # Order views
    path('orders/', views.customer_orders, name='customer_orders'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('order/<int:order_id>/success/', views.order_success, name='order_success'),
    
    # Restaurant order management
    path('restaurant/<int:restaurant_id>/orders/', views.restaurant_orders, name='restaurant_orders'),
    path('order/<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),
] 