# accounts/utils.py

from .models import ActivityLog

def log_activity(*, actor, action, customer=None):
    """
    Universal activity logger.

    actor    = User performing the action
    customer = User affected by the action (optional)
    action   = Human-readable activity text
    """
    ActivityLog.objects.create(
        actor=actor,
        customer=customer,
        action=action
    )
