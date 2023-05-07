# Simple_Store
a simple store backend created with django, drf and ...


# How to run:
1 clone the repository and pull it to your host / vps
2 run "pip install requirements"
3 config your database in storefront/settings.py ( Best options: Postgresql, Mysql, ... )
4 run "python manage.py migrate"
5 run the project using one of these:
 server     : "gunicorn --workers=6 --bind 0.0.0.0:3000 storefront.wsgi"
 localhost: : "python manage.py runserver"
