# Akima

Web application for a handmade crochet store.
Built with Django 6.0.2.

Developers: Alyson Henao, Samuel Moncada, Emily Cardona, Jose Miguel Sanchez, Juan Osorio


## System requirements

- Python 3.10 or higher
- pip (comes with Python)
- Git (to clone the repository)

## Installation

Run the following commands in order:

**1. Clone the repository**

`git clone https://github.com/AlysonHenao/Akima/`

**2. Navigate into the project folder**

`cd Akima`

**3. Create a virtual environment**

`python -m venv venv`

**4. Activate the virtual environment**

- Linux / Mac: `source venv/bin/activate`        

- Windows: `venv\Scripts\activate`

**5. Install dependencies**

`pip install -r requirements.txt`

**6. Apply database migrations**

`python manage.py migrate`

**7. Create admin superuser**

`python manage.py createsuperuser`


## Running the project

Start the development server:

`python manage.py runserver`

Open in browser:
http://127.0.0.1:8000


## User Roles and Functionalities

Akima has three user roles with different permissions:

### 👤 CLIENTE (Customer/Client)

**Access:**
- Can register and login to the platform
- Can only view products and create orders
- Cannot access admin panels

**Features:**
1. **Browse Products**: View all active products in the catalog
2. **Search Products**: Search products by name
3. **View Product Details**: See colors, sizes, prices, and manufacturing guides
4. **Add to Cart**: Add products with custom colors and sizes
5. **Manage Cart**: 
   - View items in cart
   - Update quantities
   - Remove items
6. **Create Order**: Checkout and pay for items
   - Select payment method
   - Upload payment proof/receipt
7. **Check Order Status**: View all their submitted orders and track status
8. **Receive Emails**: Get confirmation emails when orders are confirmed

**Paso a paso:**
1. Go to http://127.0.0.1:8000/register/
2. Fill registration form with your details (Try creating your account with a real email address and check it.)
3. Account automatically created as "cliente" role
4. Browse products on home page
5. Add products to cart
6. Checkout → Select payment method → Upload receipt
7. Admin will verify payment and confirm order
8. Check order status in "Órdenes" section

---

### 👨‍💼 EMPLEADO (Employee)

**Access:**
- Must be created and assigned by an admin
- Can only login if admin sets their role to "empleada"
- Cannot access customer or admin purchasing features

**Features:**
1. **View Employee Panel**: Access production dashboard
2. **View Assigned Products**: See products assigned to them
   - Check product details
   - View quantity and specifications
   - Track production status
3. **Receive Task Emails**: Automatically notified when tasks are assigned

**Paso a paso:**
1. Admin must change your role to "empleada" in admin panel
2. Go to http://127.0.0.1:8000/login/ and login with your email
3. Redirected to employee panel at http://127.0.0.1:8000/employee/
4. View assigned products and tasks
5. Check email for task notifications

---

### 🔐 ADMINISTRADOR (Administrator)

**Access:**
- Super admin account created during setup
- Full access to all functionalities
- Can manage users, products, orders, and production

**Features:**

**1. Product Management (Administrator Panel)**
- Create new products with colors, sizes, prices
- Upload product images (max 5 per product)
- Set manufacturing time and guides
- Edit existing products
- Activate/Deactivate products
- Create color catalog
- Build product sets (combinations)

**2. User Management (Django Admin)**
- View all users
- Change user roles (cliente → empleada → administrador)
- Delete users
- View user purchase history

**3. Order Management**
- View all customer orders
- Confirm payment receipts
- Change order status (pending → confirmed → shipped → delivered)
- Check order details for specific customers
- View all payment information

**4. Production Management**
- Assign products to employees
- Employees automatically notified by email
- View assigned product list
- Track production status (pending → in progress → completed)
- Monitor employee workload

**5. Payment Management**
- View all payment receipts
- Confirm/validate customer payments
- Notify customers when payment confirmed

**Paso a paso:**

**Create Products:**
1. Go to http://127.0.0.1:8000/administrator/
2. Fill in product details (name, price, category, etc.)
3. Select colors from catalog or create new colors
4. Upload product images (max 5)
5. Set manufacturing time
6. Save product

**Manage Orders:**
1. Go to http://127.0.0.1:8000/admin/ (Django Admin)
2. Click "Orders" section
3. View all pending orders
4. Click order → Update status → Save

**Confirm Payments:**
1. Go to "Órdenes" section in app
2. See all customers and their orders
3. Click customer → See pending orders with receipts
4. Upload receipt → Confirm payment
5. Customer receives confirmation email

**Assign Tasks to Employees:**
1. Go to "Producción" → "Panel de Producción"
2. Select employee from dropdown
3. Select product to assign
4. Add specifications (optional)
5. Submit
6. Employee receives email with task details

**Change User Roles:**
1. Go to http://127.0.0.1:8000/admin/
2. Go to "Users" section
3. Click on user
4. Change "Role" field to desired role (cliente, empleada, administrador)
5. Save
6. User can now login with new permissions


## Initial Setup Guide

**Step 1:** Create Superadmin Account

`python manage.py createsuperuser`

**Step 2:** Access Django Admin

Go to: http://127.0.0.1:8000/admin/
- Login with superadmin credentials created above

**Step 3:** Create Products

1. Open app: http://127.0.0.1:8000/
2. Go to "Administrador" panel (or /administrator/)
3. Create at least one product
4. Add colors and images
5. Save product

**Step 4:** Create Employee Accounts

1. In Django Admin, go to Users section
2. Create new users for employees
3. Change their role from "cliente" to "empleada"

**Step 5:** Test All Features

- Register as new client
- Browse products and create orders
- Review orders as admin
- Assign tasks to employees
- Check emails (sent via configured email service)

---

## Email Configuration (Gmail SMTP)

Emails are configured to send via Gmail. To enable:

1. Create `.env` file in project root
2. Add your Gmail credentials:
   ```
   EMAIL_HOST_USER=your_email@gmail.com
   EMAIL_HOST_PASSWORD=your_app_password
   ```
3. Generate app password at: https://myaccount.google.com/apppasswords

**Emails sent:**
- Registration confirmation (to customer)
- Task assignment (to employee)
- Payment confirmation (to customer)
- Payment notification (to admin)

---

## Project Structure

```
Akima/
├── account/          # User authentication & roles
├── product/          # Product catalog management
├── order/            # Shopping cart & orders
├── production/       # Employee tasks & manufacturing
├── templates/        # HTML templates for each section
├── media/            # Uploaded images & files
├── manage.py         # Django management commands
├── requirements.txt  # Project dependencies
└── README.md         # This file
```

---

## Troubleshooting

**Issue:** Users can't see their role-specific panels
- **Solution:** Clear browser cache and close/reopen browser

**Issue:** Emails not sending
- **Solution:** Check `.env` file has correct Gmail credentials
- Make sure 2FA is enabled on Gmail account
- Verify app password was generated correctly

**Issue:** Permission denied errors
- **Solution:** Always change role in Django Admin, not in regular admin panel
- Go to http://127.0.0.1:8000/admin/ (Django Admin)

---

## Support

For issues or questions about Akima, contact the development team.

