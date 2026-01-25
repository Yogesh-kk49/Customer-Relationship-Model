from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.contrib import admin


# ===============================
# CUSTOM USER MODEL
# ===============================
class User(AbstractUser):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("customer", "Customer"),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="customer"
    )

    profile_photo = models.ImageField(
        upload_to="profiles/",
        null=True,
        blank=True
    )

    def __str__(self):
        return self.username


# ===============================
# CUSTOMER EXTRA PROFILE
# ===============================
class Customer(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="customer_profile"
    )

    mobile = models.CharField(
        max_length=10,
        blank=True,
        null=True
    )

    profile_photo = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True
    )

    def __str__(self):
        return self.user.username


# ===============================
# BUSINESS PROFILE
# ===============================
class BusinessProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="business_profile"
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_business_profiles"
    )

    mobile = models.CharField(
        max_length=10,
        blank=True,
        null=True
    )

    business_type = models.CharField(max_length=100, blank=True)

    investment = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    expected_profit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    actual_profit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - Business Profile"


# ===============================
# LEADS
# ===============================
class Lead(models.Model):
    username = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


# ===============================
# ACTIVITY LOG
# ===============================
class ActivityLog(models.Model):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="activity_logs"
    )

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="customer_logs"
    )

    action = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.actor} - {self.action}"


# ===============================
# SUPPORT REQUEST
# ===============================
class SupportRequest(models.Model):
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="support_requests"
    )

    subject = models.CharField(max_length=100)
    message = models.TextField()
    status = models.CharField(max_length=20, default="Open")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.username} - {self.subject}"


# ===============================
# NOTIFICATIONS (ADMIN → CUSTOMER)
# ===============================
class Notification(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_notifications"
    )

    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_notifications"
    )

    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"To {self.receiver.username}: {self.message[:30]}"

# ===============================
# DIRECT MESSAGE (Customer ↔ Admin)
# ===============================
class ContactMessage(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contact_messages')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.customer.username}: {self.message[:50]}"