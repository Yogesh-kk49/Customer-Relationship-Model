from django.core.management.base import BaseCommand
from accounts.models import User, BusinessProfile


class Command(BaseCommand):
    help = (
        "Creates (or resets) the demo admin login shown on the login page: "
        "demo@gmail.com / 123. Safe to run multiple times."
    )

    def handle(self, *args, **options):
        email = "demo@gmail.com"
        password = "123"

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "username": "demo_admin",
                "role": "admin",
                "is_staff": True,
                "is_superuser": False,
            },
        )

        # Always make sure the role/password match what the login note promises,
        # even if the account already existed.
        user.role = "admin"
        user.is_staff = True
        user.set_password(password)
        user.save()

        BusinessProfile.objects.get_or_create(user=user, defaults={"mobile": "9999999999"})

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created demo admin: {email} / {password}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Demo admin already existed — password reset to '{password}'."))