from __future__ import annotations

import re
from typing import Optional, Set, Tuple

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db.models import Max
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone

from accounts.models import User
from .models import Ticket, PublicRequest
from .models_chat import (
    TicketMessage,
    TicketMessageAttachment,
    TicketMessageMention,
    TicketMessageRead,
)
from .chat_permissions import is_staff_user

MENTION_RE = re.compile(r"@([A-Za-z0-9_.-]{3,50})")


def _extract_mentions(text: str) -> Set[str]:
    return set(MENTION_RE.findall(text or ""))


def _resolve_target(kind: str, object_id: int):
    """
    kind: 'ticket' | 'public'
    """
    kind = (kind or "").lower().strip()
    if kind == "ticket":
        return get_object_or_404(Ticket, pk=object_id)
    if kind == "public":
        return get_object_or_404(PublicRequest, pk=object_id)
    raise HttpResponseForbidden("Invalid kind")


def _ct_and_object_id(target) -> Tuple[ContentType, int]:
    ct = ContentType.objects.get_for_model(target.__class__)
    return ct, int(target.pk)


def messages_for(user, target):
    """
    Returnează mesajele pentru target (Ticket/PublicRequest), filtrate după vizibilitate.
    """
    ct, obj_id = _ct_and_object_id(target)
    qs = (
        TicketMessage.objects
        .filter(content_type=ct, object_id=obj_id)
        .select_related("author", "reply_to", "content_type")
        .prefetch_related("attachments")
        .order_by("created_at")
    )
    if not is_staff_user(user):
        qs = qs.filter(visibility=TicketMessage.Visibility.PUBLIC)
    return qs


def mark_target_read(user, target, last_msg: Optional[TicketMessage]) -> None:
    """
    Setează last_read_message pentru un target (generic).
    """
    ct, obj_id = _ct_and_object_id(target)
    read_obj, _ = TicketMessageRead.objects.get_or_create(
        content_type=ct,
        object_id=obj_id,
        user=user,
        defaults={"updated_at": timezone.now()},
    )

    if last_msg:
        read_obj.last_read_message = last_msg
        read_obj.updated_at = timezone.now()
        read_obj.save(update_fields=["last_read_message", "updated_at"])


@login_required
def chat_post(request, kind: str, object_id: int):
    """
    POST mesaj + atașamente pe un target (Ticket/PublicRequest).

    URL (ex):
      /ro/portal/chat/public/10/post/
      /ro/portal/chat/ticket/55/post/
    """
    if request.method != "POST":
        return HttpResponseForbidden()

    target = _resolve_target(kind, object_id)
    ct, obj_id = _ct_and_object_id(target)

    body = (request.POST.get("body") or "").strip()
    reply_to_id = request.POST.get("reply_to") or None
    visibility = (request.POST.get("visibility") or TicketMessage.Visibility.PUBLIC).strip()

    # Client -> doar PUBLIC
    if not is_staff_user(request.user):
        visibility = TicketMessage.Visibility.PUBLIC
    else:
        if visibility not in {TicketMessage.Visibility.PUBLIC, TicketMessage.Visibility.INTERNAL}:
            visibility = TicketMessage.Visibility.PUBLIC

    # reply doar în același target (fără cross ticket/public)
    reply_to = None
    if reply_to_id:
        try:
            reply_to = TicketMessage.objects.get(
                pk=int(reply_to_id),
                content_type=ct,
                object_id=obj_id,
            )
        except (ValueError, TicketMessage.DoesNotExist):
            reply_to = None

    msg = TicketMessage.objects.create(
        content_type=ct,
        object_id=obj_id,
        author=request.user,
        body=body,
        reply_to=reply_to,
        visibility=visibility,
    )

    # atașamente (multiple)
    for f in request.FILES.getlist("attachments"):
        TicketMessageAttachment.objects.create(
            message=msg,
            file=f,
            original_name=getattr(f, "name", "") or "",
            content_type=getattr(f, "content_type", "") or "",
            size=getattr(f, "size", 0) or 0,
        )

    # mentions (după username)
    usernames = _extract_mentions(body)
    if usernames:
        mentioned = User.objects.filter(username__in=list(usernames), is_active=True)
        TicketMessageMention.objects.bulk_create(
            [TicketMessageMention(message=msg, mentioned_user=u) for u in mentioned],
            ignore_conflicts=True,
        )

    # după postare, autorul a citit până la mesajul lui
    mark_target_read(request.user, target, msg)

    next_url = request.POST.get("next")
    return redirect(next_url or request.META.get("HTTP_REFERER", "/"))


@login_required
def chat_unread_count(request):
    """
    Bulina: număr total mesaje necitite pe toate target-urile.
    Simplu și stabil: calculează per read-record (target) câte mesaje sunt după last_read.
    Pentru target-uri fără read-record, le consideră necitite (toate mesajele).

    Return: {"unread_total": <int>}
    """
    user = request.user

    msg_qs = TicketMessage.objects.all()
    if not is_staff_user(user):
        msg_qs = msg_qs.filter(visibility=TicketMessage.Visibility.PUBLIC)

    reads = (
        TicketMessageRead.objects
        .filter(user=user)
        .select_related("content_type", "last_read_message")
    )

    # 1) pentru target-uri cu record: count mesaje după last_read_message
    total = 0
    seen_pairs = set()  # (ct_id, obj_id)

    for r in reads:
        seen_pairs.add((r.content_type_id, r.object_id))
        last_id = r.last_read_message_id or 0
        total += msg_qs.filter(
            content_type_id=r.content_type_id,
            object_id=r.object_id,
            id__gt=last_id,
        ).count()

    # 2) target-uri fără record: toate mesajele sunt "unread"
    # le determinăm din mesajele existente
    all_pairs = (
        msg_qs.values_list("content_type_id", "object_id")
        .distinct()
    )

    missing_pairs = [(ct_id, obj_id) for (ct_id, obj_id) in all_pairs if (ct_id, obj_id) not in seen_pairs]
    for ct_id, obj_id in missing_pairs:
        total += msg_qs.filter(content_type_id=ct_id, object_id=obj_id).count()

    return JsonResponse({"unread_total": total})
