from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseForbidden, JsonResponse
from .models import Restaurant, Table
from .forms import RestaurantForm, TableForm
import os
import logging
from django.contrib import messages

# Get logger
logger = logging.getLogger(__name__)


def home(request):
    """
    Home page view
    """
    restaurants = Restaurant.objects.filter(is_active=True)
    return render(request, 'restaurant/home.html', {'restaurants': restaurants})


class RestaurantOwnerRequiredMixin(UserPassesTestMixin):
    """
    Mixin to check if user is a restaurant owner
    """
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_restaurant_owner


class DashboardView(RestaurantOwnerRequiredMixin, ListView):
    """
    Dashboard view for restaurant owners
    """
    model = Restaurant
    template_name = 'restaurant/dashboard.html'
    context_object_name = 'restaurants'
    
    def get_queryset(self):
        return Restaurant.objects.filter(owner=self.request.user)


class RestaurantCreateView(RestaurantOwnerRequiredMixin, CreateView):
    """
    View for creating a new restaurant
    """
    model = Restaurant
    form_class = RestaurantForm
    template_name = 'restaurant/restaurant_form.html'
    success_url = reverse_lazy('restaurant:dashboard')
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class RestaurantUpdateView(RestaurantOwnerRequiredMixin, UpdateView):
    """
    View for updating restaurant information
    """
    model = Restaurant
    form_class = RestaurantForm
    template_name = 'restaurant/restaurant_form.html'
    success_url = reverse_lazy('restaurant:dashboard')
    
    def get_queryset(self):
        return Restaurant.objects.filter(owner=self.request.user)


class RestaurantDetailView(DetailView):
    """
    Restaurant detail view
    """
    model = Restaurant
    template_name = 'restaurant/restaurant_detail.html'
    context_object_name = 'restaurant'


@login_required
def table_list(request, restaurant_id):
    """
    View tables for a restaurant
    """
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    
    # Check if the user is the owner of the restaurant
    if request.user != restaurant.owner and not request.user.is_superuser:
        return HttpResponseForbidden("You do not have permission to access this page")
    
    tables = Table.objects.filter(restaurant=restaurant)
    return render(request, 'restaurant/table_list.html', {
        'restaurant': restaurant,
        'tables': tables
    })


@login_required
def table_create(request, restaurant_id):
    """
    Create a new table
    """
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    
    # Check if the user is the owner of the restaurant
    if request.user != restaurant.owner and not request.user.is_superuser:
        return HttpResponseForbidden("You do not have permission to access this page")
    
    if request.method == 'POST':
        form = TableForm(request.POST)
        if form.is_valid():
            table = form.save(commit=False)
            table.restaurant = restaurant
            table.save()
            return redirect('restaurant:table_list', restaurant_id=restaurant.id)
    else:
        form = TableForm()
    
    return render(request, 'restaurant/table_form.html', {
        'form': form,
        'restaurant': restaurant
    })


@login_required
def table_update(request, table_id):
    """
    Update an existing table
    """
    table = get_object_or_404(Table, id=table_id)
    restaurant = table.restaurant
    
    # Check if the user is the owner of the restaurant
    if request.user != restaurant.owner and not request.user.is_superuser:
        return HttpResponseForbidden("You do not have permission to access this page")
    
    if request.method == 'POST':
        form = TableForm(request.POST, instance=table)
        if form.is_valid():
            form.save()
            return redirect('restaurant:table_list', restaurant_id=restaurant.id)
    else:
        form = TableForm(instance=table)
    
    return render(request, 'restaurant/table_form.html', {
        'form': form,
        'restaurant': restaurant,
        'table': table
    })


@login_required
def table_delete(request, table_id):
    """
    Delete a table
    """
    table = get_object_or_404(Table, id=table_id)
    restaurant = table.restaurant
    
    # Check if the user is the owner of the restaurant
    if request.user != restaurant.owner and not request.user.is_superuser:
        return HttpResponseForbidden("You do not have permission to access this page")
    
    if request.method == 'POST':
        table.delete()
        return redirect('restaurant:table_list', restaurant_id=restaurant.id)
    
    return render(request, 'restaurant/table_confirm_delete.html', {
        'table': table,
        'restaurant': restaurant
    })


@login_required
def table_qrcode(request, table_id):
    """
    View QR code for a table
    """
    table = get_object_or_404(Table, id=table_id)
    restaurant = table.restaurant
    
    # Check if the user is the owner of the restaurant
    if request.user != restaurant.owner and not request.user.is_superuser:
        return HttpResponseForbidden("You do not have permission to access this page")
    
    # If request includes regenerate parameter, regenerate QR code
    if request.GET.get('regenerate') == 'true':
        try:
            if table.qr_code:
                # Delete old QR code file
                if os.path.exists(table.qr_code.path):
                    os.remove(table.qr_code.path)
                table.qr_code = None
            # Ensure menu URL is generated and log it
            menu_url = table.menu_url
            logger.info(f"Regenerating QR code for table {table.id}, URL: {menu_url}")
            table.generate_qr_code()
            table.save(update_fields=['qr_code'])
            logger.info(f"QR code regenerated successfully for table {table.id}")
        except Exception as e:
            logger.error(f"Error regenerating QR code: {str(e)}")
        
    # Prepare context data for template
    context = {
        'table': table,
        'restaurant': restaurant,
    }
    
    # Add menu URL to context to avoid calling method in template
    context['menu_url'] = table.menu_url
    
    return render(request, 'restaurant/table_qrcode.html', context)


@login_required
def table_select(request):
    """
    Customer table selection page
    """
    # Get all active restaurants
    restaurants = Restaurant.objects.filter(is_active=True)
    
    if request.method == 'POST':
        table_id = request.POST.get('table_id')
        table = get_object_or_404(Table, id=table_id)
        
        # Redirect user to customer table view
        return redirect('restaurant:customer_table_view', table_uuid=table.uuid)
    
    return render(request, 'restaurant/table_select.html', {'restaurants': restaurants})


@login_required
def customer_table_view(request, table_uuid):
    """
    Customer table view, showing table number and QR code
    """
    table = get_object_or_404(Table, uuid=table_uuid)
    restaurant = table.restaurant
    
    # Store table_uuid in session for future ordering
    request.session['current_table_uuid'] = str(table_uuid)
    
    return render(request, 'restaurant/customer_table_view.html', {
        'table': table,
        'restaurant': restaurant,
        'menu_url': table.menu_url
    })


@login_required
def api_get_tables(request, restaurant_id):
    """
    API endpoint: Get tables for a restaurant
    """
    restaurant = get_object_or_404(Restaurant, id=restaurant_id, is_active=True)
    tables = Table.objects.filter(restaurant=restaurant, is_active=True)
    
    tables_data = [
        {
            'id': table.id,
            'name': table.name,
            'seats': table.seats,
            'uuid': str(table.uuid)
        }
        for table in tables
    ]
    
    return JsonResponse(tables_data, safe=False) 