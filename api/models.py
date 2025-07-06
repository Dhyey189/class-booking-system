from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
import pytz

from api.constants import ClassTypeChoices


class TimeStampedModel(models.Model):
    """
    An abstract model, that can be used as base model to track record's created and updated
    time.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class FitnessClass(TimeStampedModel):
    name = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    class_type = models.CharField(
        max_length=10,
        choices=ClassTypeChoices.choices,
        default=ClassTypeChoices.YOGA.value,
    )
    class_time = models.DateTimeField()
    instructor_name = models.CharField(max_length=100)
    instructor_email = models.EmailField(max_length=200)
    max_slots = models.PositiveIntegerField(
        help_text="Total number of seats/clients class can accomodate."
    )
    available_slots = models.PositiveIntegerField(
        help_text="Total number of available/unbooked seats."
    )

    def save(self, *args, **kwargs):
        if self.pk is None and not hasattr(self, "available_slots"):
            self.available_slots = self.max_slots
        super().save(*args, **kwargs)

    @property
    def is_available(self):
        return self.available_slots > 0

    def book_slot(self):
        if not self.is_available():
            raise ValidationError(
                f"No available slots for this {self.class_type} class"
            )

        self.available_slots -= 1
        self.save()


class FitnessClassBooking(TimeStampedModel):
    fitness_class = models.ForeignKey(
        FitnessClass, on_delete=models.CASCADE, related_name="bookings"
    )
    client_name = models.CharField(max_length=100)
    client_email = models.EmailField(max_length=200)

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.fitness_class.book_slot()
        super().save(*args, **kwargs)
