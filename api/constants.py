from django.db.models import TextChoices


class ClassTypeChoices(TextChoices):
    YOGA = "yoga", "Yoga"
    ZUMBA = "zumba", "Zumba"
    HIIT = "hiit", "HIIT"
