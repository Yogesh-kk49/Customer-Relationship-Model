from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Document(models.Model):
    DOCUMENT_TYPES = [
        ("bill", "Bill"),
        ("due", "Due"),
        ("report", "Customer Report"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="documents"
    )

    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_documents"
    )

    document_type = models.CharField(
        max_length=20,
        choices=DOCUMENT_TYPES
    )

    title = models.CharField(max_length=255)

    document_file = models.FileField(
        upload_to="documents/"
    )

    document_date = models.DateField(
        null=True,
        blank=True
    )

    description = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.title} - {self.user.username}"
