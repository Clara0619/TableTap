# TableTap 

TableTap is an online ordering platform based on Django, supporting customer QR code ordering, merchant backend management, and platform supervision by super users. The frontend uses Bootstrap 5, with a clean and elegant design.

## Main Features

### Customer Features
- QR Code Ordering: Scan the QR code at each table to access the menu page
- Add to Cart: Select dishes and add them to shopping cart
- Checkout and Order: Simulate payment and submit orders
- View Orders: Check personal order history and status
- Login and Registration: Use username + password to login and register
- Homepage Browsing: Browse brand introduction and menu entrance

### Merchant Features
- Backend Login: Log in to enter the merchant management system
- Create Menus: Each merchant can create multiple menus
- Manage Categories: Manage categories for each menu
- Manage Menu Items: Manage dishes under each category
- Menu Activation: Enable/disable menu status
- Create Tables: Generate unique QR code for each table
- View QR Codes: Display table QR codes for scanning
- Manage Orders: View and update order status (Preparing → Served → Completed)

### Super User Features
- Django Admin Backend: Add/edit all restaurants, users, menus, and orders
- Page Access Control: Customers cannot access backend, merchants can only manage their own data, guests cannot place orders

### QR Code Features
- Real scannable QR code images: Automatically generated QR codes
- QR code image automatically generated for each table upon saving: System backend generation, frontend display

## Technology Stack

- Backend: Django 5.0
- Frontend: Bootstrap 5
- QR Code Generation: qrcode, Pillow



2. install
```
pip install -r requirements.txt
```

3.
```
python manage.py makemigrations
python manage.py migrate
```

4. 
```
python manage.py createsuperuser
```

5. 
```
python manage.py runserver
```

## Project Structure

- `restaurant`: Restaurant management application, handles restaurant and table related functions
- `menu`: Menu management application, handles menu, category and menu item related functions
- `order`: Order management application, handles shopping cart and order related functions
- `user`: User management application, handles user authentication and authorization

## User Guide

1. Login as a superuser to the admin backend, create restaurants and merchant accounts
2. Merchants login to the system, create menus and tables
3. Generate table QR codes, print and place them on dining tables
4. Customers scan the QR codes, browse the menu and place orders
5. Merchants process orders in the backend management system