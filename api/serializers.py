from rest_framework import serializers

from api.constants import ClassTypeChoices
from api.models import FitnessClass, FitnessClassBooking
import pytz


class FitnessClassSerializer(serializers.ModelSerializer):
    """
    FitnessClass serializer to get the fitness class details based on timezone settings.
    """
    class_type_display = serializers.SerializerMethodField()

    class Meta:
        model = FitnessClass
        fields = (
            "id",
            "name",
            "description",
            "class_type",
            "class_type_display",
            "class_time",
            "instructor_name",
            "instructor_email",
            "available_slots",
            "max_slots",
            "is_available",
            "created_at",
        )

    def to_representation(self, instance):
        self.fields["class_time"] = serializers.DateTimeField(
            default_timezone=pytz.timezone(self.context["timezone"])
        )

        return super().to_representation(instance)

    def get_class_type_display(self, obj):
        return dict(ClassTypeChoices.choices)[obj.class_type]


class BookingSerializer(serializers.ModelSerializer):
    """
    FitnessClassBooking serializer to create a booking for a fitness class and list all bookings.
    """
    fitness_class_details = FitnessClassSerializer(
        source="fitness_class", read_only=True
    )
    booked_at = serializers.DateTimeField(source="created_at", read_only=True)

    class Meta:
        model = FitnessClassBooking
        fields = (
            "id",
            "fitness_class",
            "fitness_class_details",
            "client_name",
            "client_email",
            "booked_at",
        )

    def to_representation(self, instance):
        self.fields["booked_at"] = serializers.DateTimeField(
            source="created_at", default_timezone=pytz.timezone(self.context["timezone"]), read_only=True
        )

        return super().to_representation(instance)

    def validate(self, data):
        if FitnessClassBooking.objects.filter(
            fitness_class=data["fitness_class"], client_email=data["client_email"]
        ).exists():
            raise serializers.ValidationError("You have already booked this class.")

        return data
