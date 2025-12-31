from datetime import timedelta
from django.contrib.admin import AdminSite
from django.apps import apps
from django.utils import timezone

class VertixAdminSite(AdminSite):
    site_header = "Vertix"
    site_title = "Vertix Admin"
    index_title = "Dashboard"

    def each_context(self, request):
        ctx = super().each_context(request)

        ContactMessage = apps.get_model("website", "ContactMessage")
        BlogPost = apps.get_model("website", "BlogPost")
        Service = apps.get_model("website", "Service")
        Project = apps.get_model("website", "Project")
        Product = apps.get_model("website", "Product")

        last_30 = timezone.now() - timedelta(days=30)

        ctx["dashboard"] = {
            "contact_unread": ContactMessage.objects.filter(is_read=False).count(),
            "contacts_30d": ContactMessage.objects.filter(created_at__gte=last_30).count(),

            "blog_total": BlogPost.objects.count(),
            "blog_published": BlogPost.objects.filter(is_published=True).count(),

            "services_total": Service.objects.count(),
            "projects_total": Project.objects.count(),

            "products_total": Product.objects.count(),
            "products_active": Product.objects.filter(is_active=True).count(),

            "recent_contacts": ContactMessage.objects.order_by("-created_at")[:6],
            "recent_posts": BlogPost.objects.order_by("-published_at")[:6],
        }
        return ctx

vertix_admin_site = VertixAdminSite(name="vertix_admin")
