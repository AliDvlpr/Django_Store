# Simple_Store
A simple store backend created with Django, DRF, and ...

## How to Run
1. Clone the repository and pull it to your host/VPS.
2. Run `pip install -r requirements.txt`.
3. Configure your database in `storefront/settings.py`. (Best options: PostgreSQL, MySQL, ...)
4. Run `python manage.py migrate`.
5. Run `python manage.py collectstatic`.
6. Run the project using one of these:
   - Server: `gunicorn --workers=6 --bind 0.0.0.0:3000 storefront.wsgi`.
   - Localhost: `python manage.py runserver`.

## Attention
Please note that this app is currently in development and may contain errors during its launch or execution. Your cooperation in identifying and fixing any issues is greatly appreciated.

If you encounter any errors or have feedback, please feel free to contact me through my social media accounts.

Thank you for your support!
