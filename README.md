# 🧶 Akima

Web application for a handmade crochet clothing store.
Built with Django 6.

---

### 1. Clone the repository

```
git clone https://github.com/AlysonHenao/Akima/
cd Akima
```

### 2. Create a virtual environment

```
python -m venv .venv
```

### 3. Activate the virtual environment

* Windows:

```
.venv\Scripts\activate
```

* Linux / Mac:

```
source .venv/bin/activate
```

### 4. Install dependencies

```
pip install -r requirements.txt
```

### 5. Apply database migrations

```
python manage.py migrate
```

### 6. Seed the database

```
python manage.py seed_all
```

✔ This will automatically create:

* users
* products
* supplies
* inventory
* orders
* production tasks

👉 You DO NOT need to create anything manually.

---

### 7. Run the development server

```
python manage.py runserver
```

Open in your browser:

```
http://127.0.0.1:8000/
```

---

## 🔑 Test Users

Use these accounts to test the system:

| Role     | Email                                           | Password |
| -------- | ----------------------------------------------- | -------- |
| Admin    | [admin@akima.com](mailto:admin@akima.com)       | 123456   |
| Employee | [empleada@akima.com](mailto:empleada@akima.com) | 123456   |
| Customer | [cliente@akima.com](mailto:cliente@akima.com)   | 123456   |

---

# 🎯 What You Can Test

## 🛍️ Customer (Client) Flow

* Register and log into the platform
* Browse the product catalog
* Search products by name
* View detailed product information
* Select product options such as color and size
* Add products to the shopping cart
* Manage cart items (update or remove products)
* Proceed to checkout
* Select a payment method
* Upload a payment receipt
* Receive confirmation notifications
*View and track the status of their orders

## 🔐 Administrator Flow

```
/administrator/
```

* Manage users and assign roles (customer, employee, admin)
* Create new products with categories, prices, and descriptions
* Edit and update existing products
* Activate or deactivate products
* Manage product colors and variations
* View all customer orders
* Access detailed information for each order
* Confirm customer payments
* Update order status throughout the process
* Assign production tasks to employees
* Add specifications to tasks
* Notify employees about new assignments

## 🧵 Employee Flow

```
/employee/
```

* Access their personal dashboard
* View all assigned production tasks
* Access manufacturing guides
* Start a production task
* Record the initial quantity of supplies to be used
* Manage their personal inventory
* Update available supplies
* Complete a production task
* Record leftover supplies after production
* Automatically update inventory based on real consumption
* Track the status of their tasks

## 🔄 Complete System Flow

How everything connects:

* A customer places an order
* The administrator reviews and confirms the payment
* The administrator assigns the order to an employee
* The employee receives a notification
* The employee starts the production process
* Supplies are registered before manufacturing
* Remaining supplies are recorded after completion
* The system updates the inventory automatically
* The task is marked as completed
* The order continues through its lifecycle until delivery

---

# 🧠 System Architecture

* `account` → user management and roles
* `product` → product catalog
* `order` → cart, orders, payments
* `production` → tasks, supplies, inventory

---

# ⚙️ Seeder Explanation

Run:

```
python manage.py seed_all
```

This command:

1. Clears the entire database
2. Executes the product seeder
3. Creates:

   * users
   * supplies
   * inventory
   * orders
   * production tasks

This allows full system testing without manual setup.

---

# 🛠️ Email Configuration (Optional)

Create a `.env` file:

```
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
```

---

# ⚠️ Troubleshooting

### Seeder error

Make sure you ran:

```
python manage.py migrate
```

---

### Permission issues

* Ensure correct login credentials
* Clear browser cookies if needed

---

### Emails not sending

* Check `.env` configuration
* Use a Gmail App Password

---

# 📦 Project Structure

```
Akima/
├── account/
├── product/
├── order/
├── production/
├── templates/
├── media/
├── manage.py
```

---

# 👨‍💻 Developers

* Alyson Henao
* Samuel Moncada
* Emily Cardona
* Jose Sanchez
* Juan José Osorio

---

# 🔥 Final Note

This is not just an e-commerce system.
It also includes:

* production workflow
* supply tracking
* employee task management

---
