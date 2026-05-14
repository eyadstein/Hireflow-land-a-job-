from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "id",
        "username",
        "email",
        "role",
        "plan",
        "country",
        "city",
        "prefers_remote",
        "is_active",
        "is_staff",
    )

    list_filter = (
        "role",
        "plan",
        "country",
        "prefers_remote",
        "is_active",
        "is_staff",
    )

    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
        "skills",
        "desired_roles",
    )

    fieldsets = UserAdmin.fieldsets + (
        (
            "HireFlow Profile",
            {
                "fields": (
                    "role",
                    "plan",
                    "bio",
                    "skills",
                    "experience_level",
                    "desired_roles",
                    "preferred_countries",
                    "prefers_remote",
                    "city",
                    "country",
                    "linkedin",
                    "portfolio",
                    "public_key",
                    "fcm_token",
                )
            },
        ),
    )