# Class Booking System

## 1. Introduction

A lightweight SaaS for classes booking APIs built with Django that lets users see classes and book available slot for particular classes, and also allows administrators to manage classes, bookings and users.

## 2. Tech Stack

- **Django 5.2.X**: Web framework & ORM
- **Django REST Framework**: RESTful API layer
- **Docker & Docker Compose**: Containerization of all services

## 3. Installation & Setup

**Prerequisite:** Docker & Docker Compose installed

```bash
# 1. Clone repository
git clone git@github.com:Dhyey189/class-booking-system.git
cd class-booking-system

# 3. Build & start services
docker-compose build
docker-compose up

# 4. Apply migrations & create superuser
docker exec -it class-booking-django-web python manage.py migrate
docker exec -it class-booking-django-web python manage.py createsuperuser
```

## 4. Access Admin and APIs

- **Admin**: http://127.0.0.1:8000/admin/
- **APIs**: http://127.0.0.1:8000/api/

## 5. Database Tables(Models)

- **FitnessClass**: Stores details regarding different types of fitness classes available, created from admin and can be viewed by clients.
- **FitnessClassBooking**: Stores booking details(slots) for a particular fitness class.

## 6. API Endpoints

1. **GET** `/api/classes/`

   - API endpoint to fetch all available classes.

2. **POST** `/api/book/`

   - API endpoint to book a slot for a particular class.

3. **GET** `/api/bookings/?email=test@test.com`

   - API endpoint to fetch all bookings made by a particular user.
