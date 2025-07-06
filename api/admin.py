from django.contrib import admin
from api.models import FitnessClass

@admin.register(FitnessClass)
class FitnessClassAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "class_type", "class_time", "instructor_name")

