ECOMMERCE STORE - SETUP GUIDE

1. Install Python from python.org if it is not already installed.
2. Open a terminal in the folder containing manage.py.
3. Install packages:
   pip install -r requirements.txt

4. Create database tables:
   python manage.py makemigrations
   python manage.py migrate

5. Create administrator:
   python manage.py createsuperuser

6. Run the site:
   python manage.py runserver

7. Open:
   Customer website: http://127.0.0.1:8000/
   Admin panel:      http://127.0.0.1:8000/admin/

8. Log in to /admin/ and add products. Select a category, set price,
   description, image if wanted, and whether the product is available.

Notes:
- Checkout records an order; it does not take real online payments.
- This project is intended for local student/demo use. Before deployment,
  set a strong secret key, DEBUG=False, configure ALLOWED_HOSTS and HTTPS,
  and review security settings.
- If you already have an older database from a previous version, back it up
  before changing models. This starter package does not include a database file.
