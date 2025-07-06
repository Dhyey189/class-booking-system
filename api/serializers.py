from rest_framework import serializers
from django.utils import timezone

from api.constants import ClassTypeChoices
from api.models import FitnessClass, FitnessClassBooking
import pytz


class FitnessClassSerializer(serializers.ModelSerializer):
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
            "updated_at"
        )

    def to_representation(self, instance):
        self.fields['class_time'] = serializers.DateTimeField(default_timezone=pytz.timezone(self.context["timezone"]))

        return super().to_representation(instance)

    def get_class_type_display(self, obj):
        return dict(ClassTypeChoices.choices)[obj.class_type]


class BookingSerializer(serializers.ModelSerializer):
    fitness_class_details = FitnessClassSerializer(
        source="fitness_class", read_only=True
    )

    class Meta:
        model = FitnessClassBooking
        fields = (
            "id",
            "fitness_class_id",
            "fitness_class_details",
            "client_name",
            "client_email",
            "created_at",
            "updated_at"
        )

    def get_booking_time_display(self, obj):
        user_timezone = self.context.get("timezone", "Asia/Kolkata")
        try:
            tz = pytz.timezone(user_timezone)
            local_time = obj.booking_time.astimezone(tz)
            return local_time.strftime("%Y-%m-%d %H:%M %Z")
        except:
            return obj.booking_time.strftime("%Y-%m-%d %H:%M")

    def validate_class_id(self, value):
        try:
            fitness_class = FitnessClass.objects.get(pk=value)
            if not fitness_class.is_available():
                raise serializers.ValidationError("This class is fully booked.")
            if fitness_class.class_time < timezone.now():
                raise serializers.ValidationError(
                    "Cannot book a class that has already started."
                )
        except FitnessClass.DoesNotExist:
            raise serializers.ValidationError("Invalid class ID.")
        return value

    def validate(self, data):
        fitness_class = FitnessClass.objects.get(pk=data["fitness_class_id"])
        client_email = data["client_email"]

        if FitnessClassBooking.objects.filter(
            fitness_class=fitness_class, client_email=client_email
        ).exists():
            raise serializers.ValidationError("You have already booked this class.")

        return data

    def create(self, validated_data):
        return FitnessClassBooking.objects.create(**validated_data)
