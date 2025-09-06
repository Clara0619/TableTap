from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib.auth import login
from restaurant.models import Restaurant, Table
from .models import Menu, Category, MenuItem
from .forms import MenuForm, CategoryForm, MenuItemForm
from user.models import User
import uuid


def menu_view(request, table_uuid):
    """
    View menu for a table by scanning QR code
    """
    table = get_object_or_404(Table, uuid=table_uuid)
    restaurant = table.restaurant
    
    # If user is logged in, store current table UUID in session
    if request.user.is_authenticated:
        request.session['current_table_uuid'] = str(table_uuid)
    
    # Get active menus
    menus = Menu.objects.filter(restaurant=restaurant, is_active=True)
    
    if not menus.exists():
        return render(request, 'menu/no_menu.html', {'restaurant': restaurant})
    
    # Use the first active menu
    menu = menus.first()
    
    # Get categories and menu items
    categories = Category.objects.filter(menu=menu, is_active=True)
    
    context = {
        'restaurant': restaurant,
        'table': table,
        'menu': menu,
        'categories': categories,
    }
    
    return render(request, 'menu/menu.html', context)


@login_required
def menu_list(request, restaurant_id):
    """
    List menus for a restaurant
    """
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    
    # Check if the user is the owner of the restaurant
    if request.user != restaurant.owner and not request.user.is_superuser:
        return HttpResponseForbidden("You do not have permission to access this page")
    
    menus = Menu.objects.filter(restaurant=restaurant)
    
    return render(request, 'menu/menu_list.html', {
        'restaurant': restaurant,
        'menus': menus
    })


@login_required
def menu_create(request, restaurant_id):
    """
    Create a new menu
    """
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    
    # Check if the user is the owner of the restaurant
    if request.user != restaurant.owner and not request.user.is_superuser:
        return HttpResponseForbidden("You do not have permission to access this page")
    
    if request.method == 'POST':
        form = MenuForm(request.POST)
        if form.is_valid():
            menu = form.save(commit=False)
            menu.restaurant = restaurant
            menu.save()
            return redirect('menu:menu_list', restaurant_id=restaurant.id)
    else:
        form = MenuForm()
    
    return render(request, 'menu/menu_form.html', {
        'form': form,
        'restaurant': restaurant
    })


@login_required
def menu_update(request, menu_id):
    """
    Update an existing menu
    """
    menu = get_object_or_404(Menu, id=menu_id)
    restaurant = menu.restaurant
    
    # Check if the user is the owner of the restaurant
    if request.user != restaurant.owner and not request.user.is_superuser:
        return HttpResponseForbidden("You do not have permission to access this page")
    
    if request.method == 'POST':
        form = MenuForm(request.POST, instance=menu)
        if form.is_valid():
            form.save()
            return redirect('menu:menu_list', restaurant_id=restaurant.id)
    else:
        form = MenuForm(instance=menu)
    
    return render(request, 'menu/menu_form.html', {
        'form': form,
        'restaurant': restaurant,
        'menu': menu
    })


@login_required
def menu_delete(request, menu_id):
    """
    Delete a menu
    """
    menu = get_object_or_404(Menu, id=menu_id)
    restaurant = menu.restaurant
    
    # Check if the user is the owner of the restaurant
    if request.user != restaurant.owner and not request.user.is_superuser:
        return HttpResponseForbidden("You do not have permission to access this page")
    
    if request.method == 'POST':
        menu.delete()
        return redirect('menu:menu_list', restaurant_id=restaurant.id)
    
    return render(request, 'menu/menu_confirm_delete.html', {
        'menu': menu,
        'restaurant': restaurant
    })


@login_required
def category_list(request, menu_id):
    """
    List categories for a menu
    """
    menu = get_object_or_404(Menu, id=menu_id)
    restaurant = menu.restaurant
    
    # Check if the user is the owner of the restaurant
    if request.user != restaurant.owner and not request.user.is_superuser:
        return HttpResponseForbidden("You do not have permission to access this page")
    
    categories = Category.objects.filter(menu=menu)
    
    return render(request, 'menu/category_list.html', {
        'restaurant': restaurant,
        'menu': menu,
        'categories': categories
    })


@login_required
def category_create(request, menu_id):
    """
    Create a new category
    """
    menu = get_object_or_404(Menu, id=menu_id)
    restaurant = menu.restaurant
    
    # Check if the user is the owner of the restaurant
    if request.user != restaurant.owner and not request.user.is_superuser:
        return HttpResponseForbidden("You do not have permission to access this page")
    
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.menu = menu
            category.save()
            return redirect('menu:category_list', menu_id=menu.id)
    else:
        form = CategoryForm()
    
    return render(request, 'menu/category_form.html', {
        'form': form,
        'restaurant': restaurant,
        'menu': menu
    })


@login_required
def category_update(request, category_id):
    """
    Update an existing category
    """
    category = get_object_or_404(Category, id=category_id)
    menu = category.menu
    restaurant = menu.restaurant
    
    # Check if the user is the owner of the restaurant
    if request.user != restaurant.owner and not request.user.is_superuser:
        return HttpResponseForbidden("You do not have permission to access this page")
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('menu:category_list', menu_id=menu.id)
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'menu/category_form.html', {
        'form': form,
        'restaurant': restaurant,
        'menu': menu,
        'category': category
    })


@login_required
def category_delete(request, category_id):
    """
    Delete a category
    """
    category = get_object_or_404(Category, id=category_id)
    menu = category.menu
    restaurant = menu.restaurant
    
    # Check if the user is the owner of the restaurant
    if request.user != restaurant.owner and not request.user.is_superuser:
        return HttpResponseForbidden("You do not have permission to access this page")
    
    if request.method == 'POST':
        category.delete()
        return redirect('menu:category_list', menu_id=menu.id)
    
    return render(request, 'menu/category_confirm_delete.html', {
        'category': category,
        'menu': menu,
        'restaurant': restaurant
    })


@login_required
def menu_item_list(request, category_id):
    """
    List menu items for a category
    """
    category = get_object_or_404(Category, id=category_id)
    menu = category.menu
    restaurant = menu.restaurant
    
    # Check if the user is the owner of the restaurant
    if request.user != restaurant.owner and not request.user.is_superuser:
        return HttpResponseForbidden("You do not have permission to access this page")
    
    items = MenuItem.objects.filter(category=category)
    
    return render(request, 'menu/menu_item_list.html', {
        'restaurant': restaurant,
        'menu': menu,
        'category': category,
        'items': items
    })


@login_required
def menu_item_create(request, category_id):
    """
    Create a new menu item
    """
    category = get_object_or_404(Category, id=category_id)
    menu = category.menu
    restaurant = menu.restaurant
    
    # Check if the user is the owner of the restaurant
    if request.user != restaurant.owner and not request.user.is_superuser:
        return HttpResponseForbidden("You do not have permission to access this page")
    
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.category = category
            item.save()
            return redirect('menu:menu_item_list', category_id=category.id)
    else:
        form = MenuItemForm()
    
    return render(request, 'menu/menu_item_form.html', {
        'form': form,
        'restaurant': restaurant,
        'menu': menu,
        'category': category
    })


@login_required
def menu_item_update(request, item_id):
    """
    Update an existing menu item
    """
    item = get_object_or_404(MenuItem, id=item_id)
    category = item.category
    menu = category.menu
    restaurant = menu.restaurant
    
    # Check if the user is the owner of the restaurant
    if request.user != restaurant.owner and not request.user.is_superuser:
        return HttpResponseForbidden("You do not have permission to access this page")
    
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect('menu:menu_item_list', category_id=category.id)
    else:
        form = MenuItemForm(instance=item)
    
    return render(request, 'menu/menu_item_form.html', {
        'form': form,
        'restaurant': restaurant,
        'menu': menu,
        'category': category,
        'item': item
    })


@login_required
def menu_item_delete(request, item_id):
    """
    Delete a menu item
    """
    item = get_object_or_404(MenuItem, id=item_id)
    category = item.category
    menu = category.menu
    restaurant = menu.restaurant
    
    # Check if the user is the owner of the restaurant
    if request.user != restaurant.owner and not request.user.is_superuser:
        return HttpResponseForbidden("You do not have permission to access this page")
    
    if request.method == 'POST':
        item.delete()
        return redirect('menu:menu_item_list', category_id=category.id)
    
    return render(request, 'menu/menu_item_confirm_delete.html', {
        'item': item,
        'category': category,
        'menu': menu,
        'restaurant': restaurant
    }) 