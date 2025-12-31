from django.http import HttpResponseForbidden
from django.utils import timezone
from .models import BlockedIP
from .security import get_client_ip

class BlockBlockedIPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = get_client_ip(request)
        if ip:
            obj = BlockedIP.objects.filter(ip=ip, blocked_until__gt=timezone.now()).first()
            if obj:
                return HttpResponseForbidden("Acces blocat temporar.")
        return self.get_response(request)
