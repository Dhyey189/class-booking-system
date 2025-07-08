from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APITestCase
from rest_framework import status

from api.models import FitnessClass, FitnessClassBooking
from api.constants import ClassTypeChoices


class BookingCreateViewTests(APITestCase):
    """
    Test to check working of class booking API.
    """
    @classmethod
    def setUpTestData(cls):
        cls.future_class = FitnessClass.objects.create(
            name="Morning Yoga",
            description="Relaxing morning yoga session",
            class_type=ClassTypeChoices.YOGA,
            class_time=timezone.now() + timedelta(days=2),
            instructor_name="Jane Doe",
            instructor_email="jane@example.com",
            max_slots=10,
            available_slots=5,
        )

        cls.past_class = FitnessClass.objects.create(
            name="Past HIIT",
            description="High intensity interval training",
            class_type=ClassTypeChoices.HIIT,
            class_time=timezone.now() - timedelta(days=1),
            instructor_name="abc",
            instructor_email="abc@example.com",
            max_slots=20,
            available_slots=5,
        )

        cls.full_class = FitnessClass.objects.create(
            name="Full Yoga Class",
            description="Popular yoga class",
            class_type=ClassTypeChoices.YOGA,
            class_time=timezone.now() + timedelta(days=4),
            instructor_name="xyz",
            instructor_email="xyz@example.com",
            max_slots=5,
            available_slots=0,
        )

        cls.existing_booking = FitnessClassBooking.objects.create(
            fitness_class=cls.future_class,
            client_name="Existing Client",
            client_email="existing@example.com",
        )
        cls.future_class.refresh_from_db()

    def test_valid_booking_scenarios(self):
        """Test all valid booking scenarios."""
        url = reverse("api:book-class")
        initial_booking_count = FitnessClassBooking.objects.count()

        valid_test_cases = [
            {
                "name": "standard_booking",
                "data": {
                    "fitness_class": self.future_class.id,
                    "client_name": "New Client",
                    "client_email": "new@example.com",
                },
                "expected_slots": 3,
                "headers": {},
            },
            {
                "name": "booking_with_timezone",
                "data": {
                    "fitness_class": self.future_class.id,
                    "client_name": "Timezone Client",
                    "client_email": "timezone@example.com",
                },
                "expected_slots": 2,
                "headers": {"X-Timezone": "America/New_York"},
            },
        ]

        for i, test_case in enumerate(valid_test_cases):
            with self.subTest(test_case["name"]):
                response = self.client.post(
                    url, test_case["data"], format="json", **test_case["headers"]
                )
                # Assert response status
                self.assertEqual(response.status_code, status.HTTP_201_CREATED)

                # Assert booking count increased
                self.assertEqual(
                    FitnessClassBooking.objects.count(), initial_booking_count + i + 1
                )

                # Assert response structure
                expected_keys = {
                    "id",
                    "fitness_class",
                    "fitness_class_details",
                    "client_name",
                    "client_email",
                    "booked_at",
                }
                self.assertEqual(set(response.data.keys()), expected_keys)

                # Assert response data
                self.assertEqual(
                    response.data["fitness_class"], test_case["data"]["fitness_class"]
                )
                self.assertEqual(
                    response.data["client_name"], test_case["data"]["client_name"]
                )
                self.assertEqual(
                    response.data["client_email"], test_case["data"]["client_email"]
                )

                # Assert available slots updated correctly
                if test_case["data"]["fitness_class"] == self.future_class.id:
                    self.future_class.refresh_from_db()
                    self.assertEqual(
                        self.future_class.available_slots, test_case["expected_slots"]
                    )

    def test_invalid_booking_scenarios(self):
        """Test all invalid booking scenarios."""
        url = reverse("api:book-class")
        initial_booking_count = FitnessClassBooking.objects.count()

        invalid_test_cases = [
            {
                "name": "duplicate_booking",
                "data": {
                    "fitness_class": self.future_class.id,
                    "client_name": "Existing Client",
                    "client_email": "existing@example.com",
                },
                "expected_error": "You have already booked this class",
            },
            {
                "name": "past_class",
                "data": {
                    "fitness_class": self.past_class.id,
                    "client_name": "New Client",
                    "client_email": "newpast@example.com",
                },
                "expected_error": "Class already started",
            },
            {
                "name": "full_class",
                "data": {
                    "fitness_class": self.full_class.id,
                    "client_name": "New Client",
                    "client_email": "newfull@example.com",
                },
                "expected_error": "No available slots",
            },
            {
                "name": "missing_fitness_class",
                "data": {
                    "client_name": "Test Client",
                    "client_email": "test@example.com",
                },
                "expected_error": "fitness_class",
            },
            {
                "name": "missing_client_name",
                "data": {
                    "fitness_class": self.future_class.id,
                    "client_email": "test@example.com",
                },
                "expected_error": "client_name",
            },
            {
                "name": "missing_client_email",
                "data": {
                    "fitness_class": self.future_class.id,
                    "client_name": "Test Client",
                },
                "expected_error": "client_email",
            },
            {
                "name": "invalid_fitness_class_id",
                "data": {
                    "fitness_class": 99999,
                    "client_name": "Test Client",
                    "client_email": "test@example.com",
                },
                "expected_error": "fitness_class",
            },
            {
                "name": "invalid_email_format",
                "data": {
                    "fitness_class": self.future_class.id,
                    "client_name": "Test Client",
                    "client_email": "invalid-email",
                },
                "expected_error": "Enter a valid email",
            },
        ]

        for test_case in invalid_test_cases:
            with self.subTest(test_case["name"]):
                response = self.client.post(url, test_case["data"], format="json")

                # Assert response status
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

                # Assert error message contains expected error
                self.assertIn(test_case["expected_error"], str(response.data))

                # Assert booking count didn't change
                self.assertEqual(
                    FitnessClassBooking.objects.count(), initial_booking_count
                )

                # Assert available slots didn't change for the classes
                self.future_class.refresh_from_db()
                self.past_class.refresh_from_db()
                self.full_class.refresh_from_db()
                self.assertEqual(self.future_class.available_slots, 4)
                self.assertEqual(self.past_class.available_slots, 5)
                self.assertEqual(self.full_class.available_slots, 0)
