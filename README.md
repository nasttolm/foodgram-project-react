# Foodgram
Yandex educational project. Python Developer course (backend).
### Description
Grocery Assistant is a diploma project of the Yandex Python Developer course. The project is an online service and an API for it. On this service, users can publish recipes, subscribe to other users, add favorite recipes to the Favorites list, and before going to the store download a summary list of products needed to prepare one or more selected dishes.

The project is implemented on Django and DjangoRestFramework. Data access is implemented via the API.
### Implementation features
- The project is wrapped in Docker containers.
- The SPA is connected to the backend on Django via the API.
- Workflow with auto-deployment to a remote server is implemented.

### Technologies
Python 3.7
Django 2.2.19
JSON
API
Docker
Nginx
PostgreSQL
Gunicorn
JWT
### Deployment to local host
1. Установите на сервере docker и docker-compose.
2. Создайте файл /infra/.env:
```
POSTGRES_USER=django_user
```
POSTGRES_PASSWORD=mysecretpassword
```
POSTGRES_DB=django
```
DB_HOST=localhost
```
DB_PORT=5432
```
SECRET_KEY=django-insecure-6xvafd-)!1q#b@08y5thisdchuasfd
```
3. Go to the /infra
4. Run command: docker-compose up -d --buld
5. Run command: docker-compose exec backend python manage.py migrate
6. Create a docker superuser. Run command: docker-compose exec backend python manage.py migrate
7. Build static. Run command: docker-compose exec backend python manage.py collectstatic --no-input
8. Fill the database with ingredients. Run command: docker-compose exec backend python manage.py load_ingredients
9. To correctly create a recipe through the frontend, you need to create tags in the database through the admin panel.
10. The API documentation is located at: http://localhost/api/docs/redoc.html
### Authors
Anastasia Tolmacheva
