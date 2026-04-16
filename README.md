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


## Running the project

Start the development server:

`python manage.py runserver`

Open in browser:
http://127.0.0.1:8000


## Initial setup

**Step 1:** Access administrator view

Go to:

http://127.0.0.1:8000/administrator/

**Step 2:** Create products

- Add new products from the administrator interface
- Fill in required fields (name, price, etc.)
- Save each product

**Step 3:** Use the application

Once products are created, you can:

- View products on the main page
- Add products to the shopping cart
- Create orders
- View existing orders

Without creating products first, the store will appear empty.

