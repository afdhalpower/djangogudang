"""Accounts app: custom User, Role, and Profile."""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user — extends Django's built-in user (username, password, email…).

    WHY extend AbstractUser (not AbstractBaseUser)?
    AbstractUser already gives username/password/email/is_staff/is_superuser/
    permissions. We only ADD fields.
    """
    ROLE_ADMIN = "admin"
    ROLE_STAFF = "staff"
    ROLE_CHOICES = [
        (ROLE_ADMIN, "Administrator"),
        (ROLE_STAFF, "Warehouse Staff"),
    ]

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default=ROLE_STAFF,
        help_text="Determines what the user can do in the system.",
    )
    phone = models.CharField(max_length=30, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["username"]

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_admin(self):
        # Convenience flag used in templates & views
        return self.role == self.ROLE_ADMIN or self.is_superuser
