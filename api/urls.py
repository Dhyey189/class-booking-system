from django.urls import path
from .views import FitnessClassListView, BookingCreateView, BookingListView

app_name = "api"

urlpatterns = [
    path("classes/", FitnessClassListView.as_view(), name="class-list"),
    path("book/", BookingCreateView.as_view(), name="book-class"),
    path("bookings/", BookingListView.as_view(), name="booking-list"),
]
