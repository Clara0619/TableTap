from django.urls import path
from . import views

app_name = 'restaurant'

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('restaurant/create/', views.RestaurantCreateView.as_view(), name='restaurant_create'),
    path('restaurant/<int:pk>/', views.RestaurantDetailView.as_view(), name='restaurant_detail'),
    path('restaurant/<int:pk>/update/', views.RestaurantUpdateView.as_view(), name='restaurant_update'),
    path('restaurant/<int:restaurant_id>/tables/', views.table_list, name='table_list'),
    path('restaurant/<int:restaurant_id>/tables/create/', views.table_create, name='table_create'),
    path('table/<int:table_id>/update/', views.table_update, name='table_update'),
    path('table/<int:table_id>/delete/', views.table_delete, name='table_delete'),
    path('table/<int:table_id>/qrcode/', views.table_qrcode, name='table_qrcode'),
    # 顾客选择桌号页面
    path('table/select/', views.table_select, name='table_select'),
    # 顾客桌面视图，显示桌号和二维码
    path('table/customer/<uuid:table_uuid>/', views.customer_table_view, name='customer_table_view'),
    # API端点：获取餐厅的桌号
    path('api/tables/<int:restaurant_id>/', views.api_get_tables, name='api_get_tables'),
] 