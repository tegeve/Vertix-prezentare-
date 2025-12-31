import uuid
from django.utils.deprecation import MiddlewareMixin
from django.urls import resolve
from .models import PageView

EXCLUDE_PREFIXES = ("/admin", "/static", "/media", "/favicon.ico")
EXCLUDE_NAMES = {"set_language"}
COOKIE_NAME = "vx_vid"
COOKIE_MAX_AGE = 60 * 60 * 24 * 90  # 90 zile

class PageViewMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        path = request.path or ""
        if path.startswith(EXCLUDE_PREFIXES):
            return response

        try:
            match = resolve(path)
            if match.url_name in EXCLUDE_NAMES:
                return response
        except Exception:
            pass

        # visitor id din cookie sau generăm
        vid = request.COOKIES.get(COOKIE_NAME)
        try:
            visitor_uuid = uuid.UUID(vid) if vid else uuid.uuid4()
        except ValueError:
            visitor_uuid = uuid.uuid4()

        user = request.user if getattr(request, "user", None) and request.user.is_authenticated else None
        ua = (request.META.get("HTTP_USER_AGENT", "") or "")[:300]
        ref = (request.META.get("HTTP_REFERER", "") or "")[:400]

        PageView.objects.create(
            path=path[:400],
            user=user,
            visitor_id=visitor_uuid,
            method=(request.method or "")[:10],
            status_code=getattr(response, "status_code", None),
            ua=ua,
            referer=ref,
        )

        # setăm cookie dacă lipsea/era invalid
        if request.COOKIES.get(COOKIE_NAME) != str(visitor_uuid):
            response.set_cookie(
                COOKIE_NAME,
                str(visitor_uuid),
                max_age=COOKIE_MAX_AGE,
                samesite="Lax",
                secure=False,  # pune True în producție pe HTTPS
                httponly=False # poate fi False; nu e secret
            )

        return response
