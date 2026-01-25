from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .models import BusinessProfile, ActivityLog

User = get_user_model()


@receiver(post_save, sender=BusinessProfile)
def log_customer_profile_update(sender, instance, created, **kwargs):
    # Log ONLY updates, not creation
    if not created:
        ActivityLog.objects.create(
            actor=instance.user,
            action="Updated profile"
        )
