from __future__ import annotations

import re
from typing import Optional, Set, Tuple

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db.models import Max, Q
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone

from accounts.models import User
from .chat_permissions import is_staff_user
from .models import PublicRequest, Ticket
from .models_chat import (
    TicketMessage,
    TicketMessageAttachment,
    TicketMessageMention,
    TicketMessageRead,
)

# Mention = email, ex: "@client@firma.ro"
MENTION_RE = re.compile(r"@([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})")


# ============================================================
# Helpers
# ============================================================

def _extract_mentions(text: str) -> Set[str]:
    return set(MENTION_RE.findall(text or ""))


def _resolve_target(kind: str, object_id: int):
    kind = (kind or "").lower().strip()
    if kind == "ticket":
        return get_object_or_404(Ticket, pk=object_id)
    if kind == "public":
        return get_object_or_404(PublicRequest, pk=object_id)
    return HttpResponseForbidden("Invalid kind")


def _ct_and_object_id(target) -> Tuple[ContentType, int]:
    ct = ContentType.objects.get_for_model(target.__class__)
    return ct, int(target.pk)


def messages_for(user, target):
    """
    Mesaje pentru target, filtrate după vizibilitate.
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
    Marchează target ca citit până la last_msg.
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


def _user_label(u: User) -> str:
    """
    Label safe pentru UI: Company — email (sau email).
    """
    company = (getattr(u, "company_name", "") or "").strip()
    cif = (getattr(u, "company_cif", "") or "").strip()
    email = (getattr(u, "email", "") or "").strip()

    if company and cif:
        company = f"{company} (CIF {cif})"

    if company and email:
        return f"{company} — {email}"
    return email or company or f"User #{u.pk}"


# ============================================================
# Views
# ============================================================

@login_required
def chat_post(request, kind: str, object_id: int):
    """
    POST mesaj + atașamente pe un target (Ticket/PublicRequest).
    """
    if request.method != "POST":
        return HttpResponseForbidden()

    target = _resolve_target(kind, object_id)
    if isinstance(target, HttpResponseForbidden):
        return target

    ct, obj_id = _ct_and_object_id(target)

    body = (request.POST.get("body") or "").strip()
    reply_to_id = (request.POST.get("reply_to") or "").strip() or None
    visibility = (request.POST.get("visibility") or TicketMessage.Visibility.PUBLIC).strip()

    # dacă mesajul e gol și nu are fișiere -> nu postăm
    if not body and not request.FILES.getlist("attachments"):
        next_url = request.POST.get("next")
        return redirect(next_url or request.META.get("HTTP_REFERER", "/"))

    # Client -> doar PUBLIC
    if not is_staff_user(request.user):
        visibility = TicketMessage.Visibility.PUBLIC
    else:
        if visibility not in {TicketMessage.Visibility.PUBLIC, TicketMessage.Visibility.INTERNAL}:
            visibility = TicketMessage.Visibility.PUBLIC

    # reply doar în același target
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

    # creare mesaj
    msg = TicketMessage.objects.create(
        content_type=ct,
        object_id=obj_id,
        author=request.user,
        body=body,
        reply_to=reply_to,
        visibility=visibility,
    )

    # atașamente
    for f in request.FILES.getlist("attachments"):
        TicketMessageAttachment.objects.create(
            message=msg,
            file=f,
            original_name=getattr(f, "name", "") or "",
            content_type=getattr(f, "content_type", "") or "",
            size=int(getattr(f, "size", 0) or 0),
        )

    # mentions (după email)
    emails = _extract_mentions(body)
    if emails:
        mentioned = User.objects.filter(email__in=list(emails), is_active=True)
        TicketMessageMention.objects.bulk_create(
            [TicketMessageMention(message=msg, mentioned_user=u) for u in mentioned],
            ignore_conflicts=True,
        )

    # autorul a citit până la mesajul lui
    mark_target_read(request.user, target, msg)

    # opțional: marchează target actualizat
    if hasattr(target, "last_chat_at"):
        target.last_chat_at = timezone.now()
        try:
            target.save(update_fields=["last_chat_at"])
        except Exception:
            pass

    next_url = request.POST.get("next")
    return redirect(next_url or request.META.get("HTTP_REFERER", "/"))


@login_required
def chat_unread_count(request):
    """
    Badge: număr de target-uri cu mesaje necitite (vizibile) pentru user.
    """
    user = request.user

    msg_qs = TicketMessage.objects.all()
    if not is_staff_user(user):
        msg_qs = msg_qs.filter(visibility=TicketMessage.Visibility.PUBLIC)

    latest_per_target = (
        msg_qs
        .values("content_type_id", "object_id")
        .annotate(last_id=Max("id"))
    )

    reads = (
        TicketMessageRead.objects
        .filter(user=user)
        .values("content_type_id", "object_id", "last_read_message_id")
    )
    read_map = {
        (r["content_type_id"], r["object_id"]): int(r["last_read_message_id"] or 0)
        for r in reads
    }

    targets_with_unread = 0
    for row in latest_per_target:
        key = (row["content_type_id"], row["object_id"])
        last_id = int(row["last_id"] or 0)
        last_read = read_map.get(key, 0)
        if last_id > last_read:
            targets_with_unread += 1

    return JsonResponse({
        "unread_total": targets_with_unread,
        "targets_with_unread": targets_with_unread,
    })


@login_required
def chat_user_autocomplete(request):
    """
    Autocomplete pentru @mention.
    Returnăm:
      - label: ce vezi în listă
      - handle: ce se inserează după @ (email)
    """
    q = (request.GET.get("q") or "").strip()
    if len(q) < 1:
        return JsonResponse({"results": []})

    qs = (
        User.objects
        .filter(is_active=True)
        .filter(
            Q(email__icontains=q) |
            Q(company_name__icontains=q) |
            Q(company_cif__icontains=q)
        )
        .order_by("email")[:10]
    )

    results = []
    for u in qs:
        email = (getattr(u, "email", "") or "").strip()
        if not email:
            # fără email nu putem menționa corect (regex-ul tău e pe email)
            continue

        results.append({
            "id": u.id,
            "label": _user_label(u),
            "handle": email,   # ✅ IMPORTANT: JS inserează asta
            "email": email,
        })

    return JsonResponse({"results": results})
