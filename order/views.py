from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.db import transaction
from django.contrib import messages
from restaurant.models import Restaurant, Table
from menu.models import MenuItem
from .models import Order, OrderItem, Cart, CartItem


@require_POST
def add_to_cart(request):
    """
    Add item to cart via AJAX
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Please login first'}, status=401)
    
    menu_item_id = request.POST.get('menu_item_id')
    quantity = int(request.POST.get('quantity', 1))
    table_uuid = request.POST.get('table_uuid') or request.session.get('current_table_uuid')
    
    # If no table UUID is provided, return error
    if not table_uuid:
        return JsonResponse({'error': 'No table specified'}, status=400)
    
    # Get the menu item
    menu_item = get_object_or_404(MenuItem, id=menu_item_id)
    restaurant = menu_item.category.menu.restaurant
    table = get_object_or_404(Table, uuid=table_uuid)
    
    # Get or create cart for this user
    cart, created = Cart.objects.get_or_create(
        user=request.user,
        restaurant=restaurant,
        defaults={'table': table}
    )
    
    # Ensure table is set
    if not cart.table or cart.table.uuid != table.uuid:
        cart.table = table
        cart.save()
    
    # Add item to cart
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        menu_item=menu_item,
        defaults={'quantity': quantity}
    )
    
    # If item already exists, update quantity
    if not created:
        cart_item.quantity += quantity
        cart_item.save()
    
    # Return updated cart info
    return JsonResponse({
        'success': True,
        'cart_total': cart.total,
        'items_count': cart.items.count()
    })


@login_required
def view_cart(request, table_uuid=None):
    """
    View shopping cart
    """
    # If table_uuid is not provided, get from session
    if not table_uuid:
        table_uuid = request.session.get('current_table_uuid')
        # If not in session either, redirect to table selection page
        if not table_uuid:
            messages.warning(request, 'Please select a table first')
            return redirect('restaurant:table_select')
        return redirect('order:view_cart', table_uuid=table_uuid)
    
    table = get_object_or_404(Table, uuid=table_uuid)
    restaurant = table.restaurant
    
    # Save current table UUID to session
    request.session['current_table_uuid'] = str(table_uuid)
    
    try:
        cart = Cart.objects.get(user=request.user, restaurant=restaurant)
        
        # Ensure cart uses current table
        if cart.table.uuid != table.uuid:
            cart.table = table
            cart.save()
            
        cart_items = cart.items.all()
    except Cart.DoesNotExist:
        cart = None
        cart_items = []
    
    return render(request, 'order/cart.html', {
        'cart': cart,
        'cart_items': cart_items,
        'restaurant': restaurant,
        'table': table
    })


@require_POST
def update_cart(request):
    """
    Update cart item quantity via AJAX
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Please login first'}, status=401)
    
    item_id = request.POST.get('item_id')
    quantity = int(request.POST.get('quantity', 1))
    
    # Get the cart item
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    if quantity <= 0:
        cart_item.delete()
    else:
        cart_item.quantity = quantity
        cart_item.save()
    
    # Return updated cart info
    cart = cart_item.cart
    return JsonResponse({
        'success': True,
        'item_subtotal': float(cart_item.subtotal) if quantity > 0 else 0,
        'cart_total': float(cart.total),
        'items_count': cart.items.count()
    })


@require_POST
def remove_from_cart(request):
    """
    Remove item from cart via AJAX
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Please login first'}, status=401)
    
    item_id = request.POST.get('item_id')
    
    # Get the cart item
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart = cart_item.cart
    cart_item.delete()
    
    # Return updated cart info
    return JsonResponse({
        'success': True,
        'cart_total': float(cart.total),
        'items_count': cart.items.count()
    })


@login_required
def checkout(request, table_uuid):
    """
    Checkout and place order
    """
    table = get_object_or_404(Table, uuid=table_uuid)
    restaurant = table.restaurant
    
    try:
        cart = Cart.objects.get(user=request.user, restaurant=restaurant)
        cart_items = cart.items.all()
    except Cart.DoesNotExist:
        messages.error(request, 'Your cart is empty')
        return redirect('menu:menu_view', table_uuid=table_uuid)
    
    if not cart_items.exists():
        messages.error(request, 'Your cart is empty')
        return redirect('menu:menu_view', table_uuid=table_uuid)
    
    if request.method == 'POST':
        special_instructions = request.POST.get('special_instructions', '')
        
        with transaction.atomic():
            # Create order
            order = Order.objects.create(
                customer=request.user,
                restaurant=restaurant,
                table=table,
                special_instructions=special_instructions
            )
            
            # Add items to order
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    menu_item=cart_item.menu_item,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.menu_item.price
                )
            
            # Clear the cart
            cart.clear()
            
            # Update order total
            order.calculate_total()
            
            messages.success(request, 'Order submitted successfully!')
            return redirect('order:order_success', order_id=order.id)
    
    return render(request, 'order/checkout.html', {
        'cart': cart,
        'cart_items': cart_items,
        'restaurant': restaurant,
        'table': table
    })


@login_required
def order_success(request, order_id):
    """
    Order success page
    """
    order = get_object_or_404(Order, id=order_id)
    
    # Check if user is the customer who placed the order
    if request.user != order.customer and not request.user.is_superuser and not (request.user.is_restaurant_owner and request.user == order.restaurant.owner):
        return HttpResponseForbidden("You do not have permission to access this page")
    
    return render(request, 'order/order_success.html', {'order': order})


@login_required
def customer_orders(request):
    """
    View all orders for a customer
    """
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    
    return render(request, 'order/customer_orders.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    """
    View order details
    """
    order = get_object_or_404(Order, id=order_id)
    
    # Check if user is authorized to view this order
    if request.user != order.customer and not request.user.is_superuser and not (request.user.is_restaurant_owner and request.user == order.restaurant.owner):
        return HttpResponseForbidden("You do not have permission to access this page")
    
    order_items = order.items.all()
    
    return render(request, 'order/order_detail.html', {
        'order': order,
        'order_items': order_items
    })


@login_required
def restaurant_orders(request, restaurant_id):
    """
    View orders for a restaurant
    """
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    
    # Check if the user is the owner of the restaurant
    if request.user != restaurant.owner and not request.user.is_superuser:
        return HttpResponseForbidden("You do not have permission to access this page")
    
    orders = Order.objects.filter(restaurant=restaurant).order_by('-created_at')
    
    return render(request, 'order/restaurant_orders.html', {
        'restaurant': restaurant,
        'orders': orders
    })


@login_required
@require_POST
def update_order_status(request, order_id):
    """
    Update order status (restaurant owner only)
    """
    order = get_object_or_404(Order, id=order_id)
    restaurant = order.restaurant
    
    # Check if the user is the owner of the restaurant
    if request.user != restaurant.owner and not request.user.is_superuser:
        return HttpResponseForbidden("You do not have permission to access this page")
    
    status = request.POST.get('status')
    if status in dict(Order.STATUS_CHOICES):
        order.status = status
        order.save()
        messages.success(request, 'Order status updated')
    else:
        messages.error(request, 'Invalid order status')
    
    return redirect('order:restaurant_orders', restaurant_id=restaurant.id) 