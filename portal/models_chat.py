from __future__ import annotations

import os
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from django.utils.text import get_valid_filename

User = settings.AUTH_USER_MODEL


# ============================================================
# CHAT MESSAGE
# ============================================================

class TicketMessage(models.Model):
    class Visibility(models.TextChoices):
        PUBLIC = "PUBLIC", "Public (client + staff)"
        INTERNAL = "INTERNAL", "Intern (doar staff)"

    # 🔗 target generic (Ticket / PublicRequest / etc.)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    target = GenericForeignKey("content_type", "object_id")

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="chat_messages"
    )

    body = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    # reply / thread
    reply_to = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="replies"
    )

    visibility = models.CharField(
        max_length=10,
        choices=Visibility.choices,
        default=Visibility.PUBLIC
    )

    edited_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["created_at"]),
        ]

    @property
    def target_label(self) -> str:
        model = self.content_type.model if self.content_type_id else "target"
        return f"{model}:{self.object_id}"

    def __str__(self) -> str:
        return f"[{self.target_label}] {self.author_id} @ {self.created_at:%Y-%m-%d %H:%M}"


# ============================================================
# ATTACHMENTS
# ============================================================

def ticket_message_upload_to(instance: "TicketMessageAttachment", filename: str) -> str:
    """
    chat/<model>/<object_id>/<message_id>/<filename>

    ex:
    chat/ticket/12/45/poza.png
    chat/publicrequest/9/77/doc.pdf
    """
    msg = instance.message
    model = msg.content_type.model if msg.content_type_id else "target"
    safe_name = get_valid_filename(os.path.basename(filename))
    msg_id = msg.pk or "tmp"
    return f"chat/{model}/{msg.object_id}/{msg_id}/{safe_name}"


class TicketMessageAttachment(models.Model):
    message = models.ForeignKey(
        TicketMessage,
        on_delete=models.CASCADE,
        related_name="attachments"
    )

    file = models.FileField(upload_to=ticket_message_upload_to)

    original_name = models.CharField(max_length=255, blank=True)
    content_type = models.CharField(max_length=120, blank=True)
    size = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        return self.original_name or os.path.basename(self.file.name)


# ============================================================
# MENTIONS
# ============================================================

class TicketMessageMention(models.Model):
    message = models.ForeignKey(
        TicketMessage,
        on_delete=models.CASCADE,
        related_name="mentions"
    )

    mentioned_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="mentioned_in_messages"
    )

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = [("message", "mentioned_user")]
        ordering = ["created_at"]


# ============================================================
# READ TRACKING (UNREAD BADGE)
# ============================================================

class TicketMessageRead(models.Model):
    """
    Marchează ultimul mesaj citit de un user
    pentru un target (Ticket / PublicRequest / etc.)
    """

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    target = GenericForeignKey("content_type", "object_id")

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="chat_reads"
    )

    last_read_message = models.ForeignKey(
        TicketMessage,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+"
    )

    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = [("content_type", "object_id", "user")]
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["content_type", "object_id", "user"]),
        ]

    def __str__(self) -> str:
        model = self.content_type.model if self.content_type_id else "target"
        return f"read:{model}:{self.object_id} by {self.user_id}"
