# Akima

Web application for a handmade crochet store.
Built with Django 6.0.2.

Developers: Alyson Henao, Samuel Moncada, Emily Cardona, Jose Miguel Sanchez, Juan Osorio

---

## System requirements

- Python 3.10 or higher
- pip (comes with Python)
- Git (to clone the repository)

---

Installation

Run the following commands in order:

## 1. Clone the repository
git clone <repository-url>

## 2. Navigate into the project folder
cd Akima-main

## 3. Create a virtual environment
python -m venv venv

## 4. Activate the virtual environment
source venv/bin/activate        # Linux / Mac
venv\Scripts\activate           # Windows

## 5. Install dependencies
pip install -r requirements.txt

## 6. Apply database migrations
python manage.py migrate

---

Running the project

Start the development server:

python manage.py runserver

Open in browser:
http://127.0.0.1:8000

---

Initial setup

Currently, the application does not include authentication, so products must be created manually before using the main store features.

Step 1: Access administrator view

Go to:

http://127.0.0.1:8000/administrator/

Step 2: Create products

- Add new products from the administrator interface
- Fill in required fields (name, price, etc.)
- Save each product

Step 3: Use the application

Once products are created, you can:

- View products on the main page
- Add products to the shopping cart
- Create orders
- View existing orders

Without creating products first, the store will appear empty.

---

Project structure

Akima-main/
│
├── Akima/                  
│   ├── settings.py         
│   ├── urls.py             
│   ├── wsgi.py             
│   └── asgi.py             
│
├── product/                
├── account/                
├── order/                  
├── production/             
│
├── templates/              
│   └── header.html
│
├── media/                  
├── requirements.txt        
├── manage.py               
└── db.sqlite3
```



