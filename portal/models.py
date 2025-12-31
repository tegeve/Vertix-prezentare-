
from django.db import models
from django.conf import settings
from django.utils import timezone

class AbuseEvent(models.Model):
    ip = models.GenericIPAddressField(null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    path = models.CharField(max_length=255, blank=True)
    reason = models.CharField(max_length=120)
    user_agent = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(fields=["ip", "created_at"]),
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["reason", "created_at"]),
        ]

class BlockedIP(models.Model):
    ip = models.GenericIPAddressField(unique=True)
    blocked_until = models.DateTimeField()
    reason = models.CharField(max_length=120, blank=True)

    def is_active(self):
        return self.blocked_until > timezone.now()


class Ticket(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tickets")
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="assigned_tickets"
    )

    subject = models.CharField(max_length=200)
    message = models.TextField()

    status = models.ForeignKey(
        "RequestStatus",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="tickets",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.subject} ({self.status or '-'})"



class RequestStatus(models.Model):
    name = models.CharField(max_length=60, unique=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

class Technician(models.Model):
    name = models.CharField(max_length=150)
    company_name = models.CharField(max_length=255, blank=True)
    company_cif = models.CharField(max_length=50, blank=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=40, blank=True)
    address = models.CharField(max_length=255, blank=True)
    category = models.CharField(max_length=120, blank=True)

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="technician_profile"
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class PublicRequest(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="public_requests"
    )

    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    company = models.CharField(max_length=255, blank=True)
    company_cif = models.CharField(max_length=50, blank=True)

    description = models.TextField()
    status = models.ForeignKey(RequestStatus, null=True, blank=True, on_delete=models.SET_NULL)
    assigned_to = models.ForeignKey(
        Technician,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="public_requests"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.email} - {self.status or ''}".strip()


class PublicRequestAttachment(models.Model):
    request = models.ForeignKey(PublicRequest, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to="requests/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name


