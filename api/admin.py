from django.contrib import admin
from api.models import FitnessClass, FitnessClassBooking


@admin.register(FitnessClass)
class FitnessClassAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "class_type", "class_time", "instructor_name")


@admin.register(FitnessClassBooking)
class FitnessClassBookingAdmin(admin.ModelAdmin):
    list_display = ("id", "fitness_class", "client_name", "client_email", "created_at")
