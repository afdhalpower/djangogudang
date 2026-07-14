"""Accounts app: custom User, Role, and Profile.

MENTOR NOTE (Laravel -> Django):
- In Laravel you'd extend `Authenticatable` or use a package (Filament/Shield) for roles.
  In Django, the cleanest pattern is a CUSTOM USER MODEL extending `AbstractUser`.
  You MUST set `AUTH_USER_MODEL` BEFORE first migration (we did, in config/settings.py).
  Changing the user model later = painful migration, so we do it on day one.
- Role: we use a simple `role` CharField with choices instead of a full RBAC package,
  to keep learning focused. (Like a `role` enum column on users in Laravel.)
- Profile: a OneToOneField extension, exactly like Laravel's `hasOne` Profile relation.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user — extends Django's built-in user (username, password, email…).

    WHY extend AbstractUser (not AbstractBaseUser)?
    AbstractUser already gives username/password/email/is_staff/is_superuser/
    permissions. We only ADD fields. AbstractBaseUser is for when you want a
    totally custom auth (e.g. email-as-username) — overkill here.
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
    # `related_name="profile"` lets us do `user.profile` (Laravel: $user->profile)
    # and `Profile.user` back-reference. OneToOne = one profile per user.
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
        # Convenience flag used in templates & views (like Laravel policy checks)
        return self.role == self.ROLE_ADMIN or self.is_superuser
