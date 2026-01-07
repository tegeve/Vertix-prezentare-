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

        dashboard = {
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

        # ✅ DOCUMENTS (optional, doar daca app-ul exista)
        try:
            Document = apps.get_model("documents", "Document")
            DocumentType = apps.get_model("documents", "DocumentType")

            dashboard.update({
                "doc_types_total": DocumentType.objects.count(),
                "docs_total": Document.objects.count(),
                "docs_draft": Document.objects.filter(status="DRAFT").count(),
                "docs_in_progress": Document.objects.filter(status="IN_PROGRESS").count(),
                "docs_ready": Document.objects.filter(status="READY").count(),
                "docs_final": Document.objects.filter(status="FINAL").count(),
                "docs_30d": Document.objects.filter(created_at__gte=last_30).count(),
                "recent_docs": Document.objects.select_related("doc_type", "client_user", "owner").order_by("-created_at")[:8],
            })
        except LookupError:
            # app "documents" nu e instalat inca
            pass

        ctx["dashboard"] = dashboard
        return ctx

vertix_admin_site = VertixAdminSite(name="vertix_admin")
