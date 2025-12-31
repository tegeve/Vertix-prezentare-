from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin
from django.utils import timezone
from django.core.exceptions import PermissionDenied

from website.admin_site import vertix_admin_site
from .models import User


@admin.register(User, site=vertix_admin_site)
class UserAdmin(BaseUserAdmin):
    ordering = ("email",)
    list_display = ("email", "role", "company_name", "is_active", "is_staff", "approved_at")
    list_filter = ("role", "is_active", "is_staff")
    search_fields = ("email", "company_name", "company_cif")
    actions = ["approve_users"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Company", {"fields": ("company_name", "company_cif")}),
        ("Role & Access", {"fields": ("role", "is_active", "is_staff", "is_superuser")}),
        ("Approval", {"fields": ("approved_at", "approved_by")}),
        ("Permissions", {"fields": ("groups", "user_permissions")}),
        ("Dates", {"fields": ("last_login", "date_joined")}),
    )
    readonly_fields = ("approved_at", "approved_by", "date_joined", "last_login")

    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "password1", "password2", "role", "is_staff", "is_active")}),
    )

    def approve_users(self, request, queryset):
        if not (request.user.role in [User.Role.ADMIN, User.Role.MANAGER] or request.user.is_superuser):
            raise PermissionDenied("Nu ai drepturi de aprobare.")
        now = timezone.now()
        updated = queryset.filter(is_active=False).update(
            is_active=True, approved_at=now, approved_by=request.user
        )
        self.message_user(request, f"Aprobate: {updated} cont(uri).")

    approve_users.short_description = "Approve selected users"


# ✅ ca să apară și "Grupuri" în admin-ul custom
vertix_admin_site.register(Group, GroupAdmin)
