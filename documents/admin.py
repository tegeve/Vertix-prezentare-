from django import forms
from django.contrib import admin
from django.db.models import Q
from tinymce.widgets import TinyMCE

from website.admin_site import vertix_admin_site
from accounts.models import User
from .models import DocumentType, Document, DocumentTerms



@admin.register(DocumentType, site=vertix_admin_site)
class DocumentTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "series", "next_number", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "code", "series")
    ordering = ("name",)

    fieldsets = (
        ("General", {"fields": ("name", "code", "is_active", "terms")}),
        ("Numerotare", {"fields": ("series", "next_number")}),
        ("Template-uri", {"fields": ("docx_template", "html_template")}),
        ("Schema formular", {"fields": ("schema_json",)}),
    )


@admin.register(Document, site=vertix_admin_site)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("number", "doc_type", "status", "client_user", "owner", "created_at")
    list_filter = ("status", "doc_type")
    search_fields = ("number", "client_user__email", "client_user__company_name", "owner__email")
    ordering = ("-created_at",)
    autocomplete_fields = ("client_user", "owner", "technicians")
    readonly_fields = ("number", "created_at", "created_by", "docx_file", "pdf_file")

    fieldsets = (
        ("Identificare", {"fields": ("doc_type", "number", "status")}),
        ("Asignare", {"fields": ("client_user", "owner", "technicians")}),
        ("Date document", {"fields": ("data_json",)}),
        ("Fișiere generate", {"fields": ("docx_file", "pdf_file")}),
        ("Audit", {"fields": ("created_by", "created_at")}),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related("doc_type", "client_user", "owner")
        u = request.user

        # Admin vede tot
        if u.role == User.Role.ADMIN:
            return qs

        # Manager vede tot (sau poți restrânge la owner dacă vrei)
        if u.role == User.Role.MANAGER:
            return qs

        # Tehnician vede doar documentele unde e asignat
        if u.role == User.Role.TEHNICIAN:
            return qs.filter(technicians=u)

        # Client nu are ce căuta în admin
        return qs.none()

    def has_module_permission(self, request):
        # Ascunde complet modulul "documents" pentru client
        return request.user.is_authenticated and request.user.role != User.Role.CLIENT

    def has_view_permission(self, request, obj=None):
        u = request.user
        if not u.is_authenticated:
            return False
        if u.role in [User.Role.ADMIN, User.Role.MANAGER]:
            return True
        if u.role == User.Role.TEHNICIAN:
            if obj is None:
                return True
            return obj.technicians.filter(pk=u.pk).exists()
        return False

    def has_change_permission(self, request, obj=None):
        u = request.user
        if not u.is_authenticated:
            return False
        if u.role in [User.Role.ADMIN, User.Role.MANAGER]:
            return True
        if u.role == User.Role.TEHNICIAN:
            if obj is None:
                return True
            # tehnician poate edita doar dacă nu e FINAL/CANCELLED
            return obj.technicians.filter(pk=u.pk).exists() and obj.status in ["DRAFT", "IN_PROGRESS", "READY"]
        return False

    def has_add_permission(self, request):
        # doar manager/admin creează documente
        return request.user.is_authenticated and request.user.role in [User.Role.ADMIN, User.Role.MANAGER]

    def has_delete_permission(self, request, obj=None):
        # de obicei doar admin (opțional)
        return request.user.is_authenticated and request.user.role == User.Role.ADMIN


class DocumentTermsAdminForm(forms.ModelForm):
    body_html = forms.CharField(widget=TinyMCE(attrs={"cols": 80, "rows": 30}))
    class Meta:
        model = DocumentTerms
        fields = "__all__"

@admin.register(DocumentTerms, site=vertix_admin_site)
class DocumentTermsAdmin(admin.ModelAdmin):
    form = DocumentTermsAdminForm
    list_display = ("key", "title", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("key", "title", "body_html")
    ordering = ("key",)
