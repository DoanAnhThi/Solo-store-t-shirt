Dockerized development
======================

Services
--------
- backend: Django app on port 8000
- frontend: Static site server on port 8080

Prerequisites
-------------
- Docker Desktop installed and running

Usage
-----

Start services:

```
docker compose up -d --build
```

Open:
- Frontend: http://localhost:8080
- Django Admin: http://127.0.0.1:8000/admin/

Create superuser (first time):

```
docker compose exec backend python manage.py createsuperuser
```

Run migrations:

```
docker compose exec backend python manage.py migrate
```

View logs:

```
docker compose logs -f backend
docker compose logs -f frontend
```

Stop services:

```
docker compose down
```

# CWISH Backend - Django E-commerce API

A Django REST Framework based e-commerce backend API.

## Features

- Product management with categories, variants, and options
- Order management system
- RESTful API endpoints
- Admin interface for content management
- CORS support for frontend integration

## Setup

### Prerequisites

- Python 3.8+
- pip

### Installation

1. Create and activate virtual environment:
```bash
python3 -m venv django_env
source django_env/bin/activate  # On Windows: django_env\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

4. Create superuser (optional):
```bash
python manage.py createsuperuser
```

5. Seed demo data:
```bash
python manage.py seed_data
```

6. Run development server:
```bash
python manage.py runserver 0.0.0.0:9000
```

## API Endpoints

### Products
- `GET /api/products/` - List all products
- `GET /api/products/{id}/` - Get product details
- `GET /api/products/{id}/variants/` - Get product variants
- `GET /api/products/{id}/images/` - Get product images

### Categories
- `GET /api/categories/` - List all categories
- `GET /api/categories/{id}/` - Get category details
- `GET /api/categories/{id}/products/` - Get products in category

### Variants
- `GET /api/variants/` - List all variants
- `GET /api/variants/{id}/` - Get variant details

### Orders
- `GET /api/orders/` - List all orders
- `GET /api/orders/{id}/` - Get order details
- `POST /api/orders/` - Create new order
- `PATCH /api/orders/{id}/update_status/` - Update order status

### Health Check
- `GET /health/` - Health check endpoint

## Admin Interface

Access the admin interface at `http://localhost:9000/admin/` to manage:
- Categories
- Products
- Product Images
- Product Options
- Product Variants
- Orders
- Order Items

## Frontend Integration

The API supports CORS and can be integrated with any frontend framework. The frontend can be served from:
- http://localhost:8080 (static files)
- http://localhost:3000 (development server)

## Database

The project uses SQLite by default for development. For production, consider using PostgreSQL or MySQL.

## Development

### Running Tests
```bash
python manage.py test
```

### Making Changes
1. Make changes to models
2. Create migrations: `python manage.py makemigrations`
3. Apply migrations: `python manage.py migrate`
4. Test your changes

## Production Deployment

For production deployment:
1. Set `DEBUG = False` in settings.py
2. Configure a production database
3. Set up static file serving
4. Use a production WSGI server like Gunicorn
5. Set up proper CORS settings
