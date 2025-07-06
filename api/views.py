from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.db.models import Q
from api.models import FitnessClass, FitnessClassBooking
from api.serializers import FitnessClassSerializer, BookingSerializer
import pytz
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class FitnessClassListView(generics.ListAPIView):
    serializer_class = FitnessClassSerializer

    def get_queryset(self):
        return FitnessClass.objects.filter(class_time__gte=timezone.now()).order_by(
            "class_time"
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["timezone"] = self.request.headers.get("X-Timezone", settings.TIME_ZONE)
        
        return context


class BookingCreateView(generics.CreateAPIView):
    serializer_class = BookingSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        user_timezone = self.request.headers.get("X-Timezone", "Asia/Kolkata")
        context["timezone"] = user_timezone
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            try:
                booking = serializer.save()
                logger.info(f"Booking created successfully for {booking.client_email}")

                return Response(
                    {
                        "status": "success",
                        "message": "Booking confirmed",
                        "booking": BookingSerializer(
                            booking, context=self.get_serializer_context()
                        ).data,
                    },
                    status=status.HTTP_201_CREATED,
                )
            except Exception as e:
                logger.error(f"Error creating booking: {str(e)}")
                return Response(
                    {"status": "error", "message": "Failed to create booking"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        else:
            logger.warning(f"Invalid booking data: {serializer.errors}")
            return Response(
                {"status": "error", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )


class BookingListView(generics.ListAPIView):
    serializer_class = BookingSerializer

    def get_queryset(self):
        email = self.request.query_params.get("email", None)
        if email:
            return FitnessClassBooking.objects.filter(client_email=email).order_by("-booking_time")
        return FitnessClassBooking.objects.none()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        user_timezone = self.request.headers.get("X-Timezone", "Asia/Kolkata")
        context["timezone"] = user_timezone
        return context

    def list(self, request, *args, **kwargs):
        email = request.query_params.get("email", None)

        if not email:
            return Response(
                {"status": "error", "message": "Email parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)

            logger.info(f"Retrieved {queryset.count()} bookings for {email}")

            return Response(
                {
                    "status": "success",
                    "email": email,
                    "count": queryset.count(),
                    "bookings": serializer.data,
                }
            )
        except Exception as e:
            logger.error(f"Error retrieving bookings: {str(e)}")
            return Response(
                {"status": "error", "message": "Failed to retrieve bookings"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
