from django import forms
from django.contrib import admin
from tinymce.widgets import TinyMCE

from .admin_site import vertix_admin_site
from .models import Industry, Service, Project, Post, Job, ContactMessage, AboutPage, PopUpMessage, BlogPost, BlogPostImage

@admin.register(Industry, site=vertix_admin_site)
class IndustryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "slug")
    list_display = ("name", "slug")

@admin.register(Service, site=vertix_admin_site)
class ServiceAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("title", "slug", "is_featured", "icon")
    list_filter = ("is_featured",)
    search_fields = ("title", "slug", "short", "description", "icon")
    ordering = ("title",)

@admin.register(Project, site=vertix_admin_site)
class ProjectAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("title", "industry", "is_featured")
    list_filter = ("industry", "is_featured")
    search_fields = ("title", "summary", "description")
    list_select_related = ("industry",)
    autocomplete_fields = ("industry",)

@admin.register(Post, site=vertix_admin_site)
class PostAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("title", "published_at")
    list_filter = ("published_at",)
    search_fields = ("title", "excerpt", "content")
    date_hierarchy = "published_at"
    ordering = ("-published_at",)

@admin.register(Job, site=vertix_admin_site)
class JobAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("title", "location", "is_active")
    list_filter = ("is_active", "location")
    search_fields = ("title", "location", "description")
    ordering = ("-is_active", "title")

@admin.register(ContactMessage, site=vertix_admin_site)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "company", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("name", "email", "company", "phone", "message")
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"
    ordering = ("-created_at",)

@admin.register(AboutPage, site=vertix_admin_site)
class AboutPageAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Hero", {"fields": ("hero_title", "hero_subtitle", "hero_image", "tone")}),
        ("Poveste", {"fields": ("story_title", "story_text", "story_image")}),
        ("Misiune / Viziune / Valori", {"fields": (
            "mission_title", "mission_text", "mission_image",
            "vision_title", "vision_text", "vision_image",
            "values_title", "values_text", "values_image",
        )}),
        ("Diferențiatori", {"fields": ("differentiators_title", "differentiators_text", "differentiators_image")}),
        ("CTA", {"fields": ("cta_title", "cta_text", "cta_button_text", "cta_button_url", "cta_image")}),
    )

@admin.register(PopUpMessage, site=vertix_admin_site)
class PopUpMessageAdmin(admin.ModelAdmin):
    list_display = ("title", "style", "is_enabled", "start_at", "end_at", "priority", "is_preset")
    list_filter = ("is_enabled", "style", "is_preset")
    search_fields = ("title", "body", "preset_key")
    ordering = ("priority", "-created_at")
    list_editable = ("is_enabled", "priority")

class BlogPostAdminForm(forms.ModelForm):
    content = forms.CharField(widget=TinyMCE(attrs={"cols": 80, "rows": 30}))
    class Meta:
        model = BlogPost
        fields = "__all__"

class BlogPostImageInline(admin.TabularInline):
    model = BlogPostImage
    extra = 1
    fields = ("image", "caption", "sort_order")
    ordering = ("sort_order",)

@admin.register(BlogPost, site=vertix_admin_site)
class BlogPostAdmin(admin.ModelAdmin):
    form = BlogPostAdminForm
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("title", "is_published", "published_at")
    list_filter = ("is_published", "published_at")
    search_fields = ("title", "short", "content")
    date_hierarchy = "published_at"
    ordering = ("-published_at",)
    inlines = [BlogPostImageInline]
    fieldsets = (
        ("Conținut", {"fields": ("title", "slug", "short", "content")}),
        ("Media", {"fields": ("image",)}),
        ("Publicare", {"fields": ("is_published", "published_at")}),
    )
