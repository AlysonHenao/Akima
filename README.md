# Akima

Web apliccation for a handmade crochet store.
Built with Django 6.0.2.

**Developers:** Alyson Henao, Samuel Moncada, Emily Cardona, Jose Miguel Sanchez, Juan Osorio



## System requirements

- Python 3.10 or higher
- pip (comes with Python)
- Git (to clone the repository)

---

## Installation

Run the following commands in order:

```bash
# 1. Clone the repository
git clone <repository-url>

# 2. Navigate into the project folder
cd Akima-main

# 3. Create a virtual environment
#    This keeps project dependencies isolated from your system Python.
python -m venv venv

# 4. Activate the virtual environment
source venv/bin/activate        # Linux / Mac
venv\Scripts\activate           # Windows

# 5. Install all required dependencies
#    Reads requirements.txt and installs every listed package.
pip install -r requirements.txt

# 6. Apply database migrations
#    Creates all tables in db.sqlite3 based on the app models.
python manage.py migrate

```

---

## Running the program

### Start the development server

```bash
python manage.py runserver
```

Opens the app at: http://127.0.0.1:8000



## Project structure

```
Akima-main/
│
├── Akima/                  # Central project configuration
│   ├── settings.py         # Database, installed apps, media config
│   ├── urls.py             # Root URLs — includes each app's URLs
│   ├── wsgi.py             # WSGI entry point for deployment
│   └── asgi.py             # ASGI entry point for async deployment
│
├── product/                # Product app
├── account/                # User and employee app
├── order/                  # Orders and payments app
├── production/             # Manufacturing and supplies app
│
├── templates/              # Shared global templates
│   └── header.html
│
├── media/                  # User-uploaded files (images, PDFs)
├── requirements.txt        # Project dependencies
├── manage.py               # Django command-line utility
└── db.sqlite3              # SQLite database file
```



