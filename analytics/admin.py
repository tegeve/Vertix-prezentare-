from datetime import timedelta

from django.contrib import admin
from django.urls import path
from django.utils import timezone
from django.template.response import TemplateResponse
from django.db.models import Count
from django.db.models.functions import TruncDate

from website.admin_site import vertix_admin_site
from .models import PageView


@admin.register(PageView, site=vertix_admin_site)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ("path", "user", "status_code", "created_at")
    list_filter = ("status_code", "created_at")
    search_fields = ("path", "ua", "referer")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    readonly_fields = ("path", "method", "status_code", "user", "ua", "referer", "created_at", "visitor_id")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


def analytics_view(request):
    # perioadă
    try:
        days = int(request.GET.get("days", 30))
    except ValueError:
        days = 30
    days = max(7, min(days, 365))
    since = timezone.now() - timedelta(days=days)

    qs = PageView.objects.filter(created_at__gte=since)

    # total accesări
    total_views = qs.count()

    # detectăm dacă există visitor_id (ca să nu crape dacă încă nu ai migrarea)
    has_visitor_id = any(f.name == "visitor_id" for f in PageView._meta.get_fields())

    # vizitatori unici
    unique_visitors = (
        qs.exclude(visitor_id__isnull=True).values("visitor_id").distinct().count()
        if has_visitor_id else None
    )

    # top pagini
    top_pages = (
        qs.values("path")
        .annotate(total=Count("id"))
        .order_by("-total")[:20]
    )

    # accesări pe zi (cross-db)
    daily_views = (
        qs.annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(total=Count("id"))
        .order_by("day")
    )

    # unici pe zi (cross-db)
    daily_unique = None
    if has_visitor_id:
        daily_unique = (
            qs.exclude(visitor_id__isnull=True)
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(unique=Count("visitor_id", distinct=True))
            .order_by("day")
        )

    ctx = vertix_admin_site.each_context(request)
    ctx.update({
        "title": "Analytics",
        "days": days,
        "since": since,

        "total_views": total_views,
        "unique_visitors": unique_visitors,
        "has_visitor_id": has_visitor_id,

        "top_pages": list(top_pages),
        "daily_views": list(daily_views),
        "daily_unique": list(daily_unique) if daily_unique is not None else None,
    })
    return TemplateResponse(request, "admin/analytics_dashboard.html", ctx)


# injectăm url în AdminSite (păstrăm pattern-ul tău)
orig_get_urls = vertix_admin_site.get_urls

def get_urls():
    urls = orig_get_urls()
    custom = [
        path("analytics/", vertix_admin_site.admin_view(analytics_view), name="analytics-dashboard"),
    ]
    return custom + urls

vertix_admin_site.get_urls = get_urls
