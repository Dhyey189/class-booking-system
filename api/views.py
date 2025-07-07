from rest_framework import generics
from django.utils import timezone
from api.models import FitnessClass, FitnessClassBooking
from api.serializers import FitnessClassSerializer, BookingSerializer
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class TimezoneContextMixin:
    """
    Class to set timezone context for view and serializer.

    If timezone is provided in the headers from frontend then all the dates like
    class date, booking date etc. will be in that timezone, or else it will be in default
    timezone as configured in settings.py
    """
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["timezone"] = self.request.headers.get("X-Timezone", settings.TIME_ZONE)

        return context


class FitnessClassListView(TimezoneContextMixin, generics.ListAPIView):
    """
    APIEndpoint to list all available fitness classes.
    """
    serializer_class = FitnessClassSerializer

    def get_queryset(self):
        return FitnessClass.objects.filter(class_time__gte=timezone.now()).order_by(
            "class_time"
        )


class BookingCreateView(TimezoneContextMixin, generics.CreateAPIView):
    """
    APIEndpoint to create a new fitness class booking.
    """
    serializer_class = BookingSerializer


class BookingListView(TimezoneContextMixin, generics.ListAPIView):
    """
    APIEndpoint to list all bookings.
    If email is provided in the query parameter, it will filter the bookings by that email
    Else it will return all bookings.
    """
    serializer_class = BookingSerializer

    def get_queryset(self):
        email = self.request.query_params.get("email", None)
        if email:
            return FitnessClassBooking.objects.filter(client_email=email).order_by(
                "-created_at"
            )

        return FitnessClassBooking.objects.all()
