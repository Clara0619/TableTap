from django.urls import path
from . import views

app_name = 'menu'

urlpatterns = [
    # Menu view by QR code
    path('table/<uuid:table_uuid>/', views.menu_view, name='menu_view'),
    
    # Restaurant owner menu management
    path('restaurant/<int:restaurant_id>/menus/', views.menu_list, name='menu_list'),
    path('restaurant/<int:restaurant_id>/menus/create/', views.menu_create, name='menu_create'),
    path('menu/<int:menu_id>/update/', views.menu_update, name='menu_update'),
    path('menu/<int:menu_id>/delete/', views.menu_delete, name='menu_delete'),
    
    # Category management
    path('menu/<int:menu_id>/categories/', views.category_list, name='category_list'),
    path('menu/<int:menu_id>/categories/create/', views.category_create, name='category_create'),
    path('category/<int:category_id>/update/', views.category_update, name='category_update'),
    path('category/<int:category_id>/delete/', views.category_delete, name='category_delete'),
    
    # Menu item management
    path('category/<int:category_id>/items/', views.menu_item_list, name='menu_item_list'),
    path('category/<int:category_id>/items/create/', views.menu_item_create, name='menu_item_create'),
    path('item/<int:item_id>/update/', views.menu_item_update, name='menu_item_update'),
    path('item/<int:item_id>/delete/', views.menu_item_delete, name='menu_item_delete'),
] 