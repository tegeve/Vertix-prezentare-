from .site_settings import get_site_settings
from django.utils import timezone
from .models import PopUpMessage
from django.db.models import Q

def site_settings(request):
    return {"site_settings": get_site_settings()}


def popup_messages(request):
    now = timezone.now()

    qs = PopUpMessage.objects.filter(is_enabled=True).filter(
        Q(start_at__isnull=True) | Q(start_at__lte=now),
        Q(end_at__isnull=True) | Q(end_at__gte=now),
    ).order_by("priority", "-created_at")

    return {"popup_messages": list(qs[:3])}  # sau [:1]