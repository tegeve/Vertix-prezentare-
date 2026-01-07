from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from portal.forms_public_request import PublicRequestForm
from portal.models import PublicRequestAttachment

from .site_settings import get_site_settings
from .forms import PopUpMessageForm

from .models import (
    AboutPage,
    BlogPost,
    Brand,
    Industry,
    Job,
    PopUpMessage,
    Product,
    ProductCategory,
    Project,
    Service,
)

# ============================================================
# Public pages
# ============================================================

def home(request):
    s = get_site_settings()
    services = Service.objects.filter(is_featured=True)[:6]
    projects = Project.objects.filter(is_featured=True)[:6]
    return render(request, "website/home.html", {
        "site_settings": s,
        "services": services,
        "projects": projects,
    })


def about(request):
    s = get_site_settings()
    if not s.about_enabled:
        return redirect("home")

    about_obj = AboutPage.objects.first()
    if not about_obj:
        about_obj = AboutPage.objects.create(
            story_text="Vertix a apărut din dorința de a crea soluții digitale clare, eficiente și ușor de folosit.",
            mission_text="Să livrăm soluții digitale care aduc rezultate reale, nu doar cod.",
            vision_text="Să fim partenerul de încredere pentru companiile care cresc prin tehnologie.",
            values_text="Transparență\nCalitate\nResponsabilitate\nOrientare spre client",
            differentiators_text="Soluții personalizate, nu copy-paste\nComunicare clară și constantă\nAccent pe rezultate\nSuport după lansare",
        )

    return render(request, "website/about.html", {
        "site_settings": s,
        "about": about_obj,
    })


def services_list(request):
    s = get_site_settings()
    if not s.services_enabled:
        return redirect("home")

    services = Service.objects.all()
    return render(request, "website/services_list.html", {
        "site_settings": s,
        "services": services,
    })


def service_detail(request, slug):
    s = get_site_settings()
    if not s.services_enabled:
        return redirect("home")

    service = get_object_or_404(Service, slug=slug)
    return render(request, "website/service_detail.html", {
        "site_settings": s,
        "service": service,
    })


def projects_list(request):
    s = get_site_settings()
    if not s.projects_enabled:
        return redirect("home")

    projects = Project.objects.select_related("industry").all()
    industries_qs = Industry.objects.all()

    active = request.GET.get("industry")
    if active:
        projects = projects.filter(industry__slug=active)

    return render(request, "website/projects_list.html", {
        "site_settings": s,
        "projects": projects,
        "industries": industries_qs,
        "active_industry": active,
    })


def project_detail(request, slug):
    s = get_site_settings()
    if not s.projects_enabled:
        return redirect("home")

    project = get_object_or_404(Project.objects.select_related("industry"), slug=slug)
    return render(request, "website/project_detail.html", {
        "site_settings": s,
        "project": project,
    })


def industries(request):
    s = get_site_settings()
    if not s.industries_enabled:
        return redirect("home")

    # Dacă vrei din DB:
    industries_qs = Industry.objects.all()

    # Dacă vrei și conținut static "pains" + linkuri:
    pains = [
        {"title": "Downtime & opriri neplanificate", "desc": "Diagnostic rapid, reparații, mentenanță și prevenție."},
        {"title": "Echipamente vechi (end-of-life)", "desc": "Retrofit + modernizare pentru fiabilitate și compatibilitate."},
        {"title": "Lipsă vizibilitate în producție", "desc": "Monitorizare, SCADA, rapoarte automate și indicatori."},
        {"title": "Calitate & trasabilitate", "desc": "Colectare date, validări, loguri și raportare."},
        {"title": "Procese birocratice lente", "desc": "RPA pentru rapoarte, comenzi, facturi, stocuri și notificări."},
        {"title": "Integrare între sisteme", "desc": "Conectăm date între sisteme existente (unde e cazul)."},
    ]

    service_links = [
        {"label": "Automatizări industriale (PLC / HMI / SCADA)", "url": reverse("services_list")},
        {"label": "Mentenanță industrială", "url": reverse("services_list")},
        {"label": "Reparații electronice industriale", "url": reverse("services_list")},
        {"label": "Reparații mecanice & intervenții", "url": reverse("services_list")},
        {"label": "Retrofit & modernizare", "url": reverse("services_list")},
        {"label": "Automatizare procese (RPA / workflow)", "url": reverse("services_list")},
        {"label": "IT industrial & integrare sisteme", "url": reverse("services_list")},
    ]

    return render(request, "website/industries.html", {
        "site_settings": s,
        "industries": industries_qs,
        "pains": pains,
        "service_links": service_links,
    })


def contact(request):
    s = get_site_settings()
    if not getattr(s, "contact_enabled", True):
        return redirect("home")

    initial = {}
    if request.user.is_authenticated:
        initial = {
            "email": request.user.email,
            "company": getattr(request.user, "company_name", "") or "",
            "company_cif": getattr(request.user, "company_cif", "") or "",
        }

    if request.method == "POST":
        form = PublicRequestForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user if request.user.is_authenticated else None

            # dacă user e logat și nu a schimbat email-ul
            if initial.get("email") and not getattr(obj, "email", None):
                obj.email = initial["email"]

            obj.save()

            for f in request.FILES.getlist("attachments"):
                PublicRequestAttachment.objects.create(request=obj, file=f)

            messages.success(request, "Cererea a fost înregistrată. Revenim cât mai curând.")
            return redirect("contact")
    else:
        form = PublicRequestForm(initial=initial)

    return render(request, "website/contact.html", {
        "site_settings": s,
        "form": form,
    })


def careers(request):
    s = get_site_settings()
    if not s.careers_enabled:
        return redirect("home")

    jobs = Job.objects.filter(is_active=True)
    return render(request, "website/careers.html", {
        "site_settings": s,
        "jobs": jobs,
    })


def gdpr(request):
    s = get_site_settings()
    if not s.gdpr_enabled:
        return redirect("home")
    return render(request, "website/gdpr.html", {"site_settings": s})


def cookies(request):
    s = get_site_settings()
    if not s.cookies_enabled:
        return redirect("home")
    return render(request, "website/cookies.html", {"site_settings": s})


# ============================================================
# Products
# ============================================================

def products_list(request):
    s = get_site_settings()

    qs = Product.objects.filter(is_active=True)

    category = request.GET.get("cat") or ""
    brand = request.GET.get("brand") or ""
    availability = request.GET.get("avail") or ""
    q = request.GET.get("q") or ""

    if category:
        qs = qs.filter(category__slug=category)
    if brand:
        qs = qs.filter(brand__name=brand)
    if availability:
        qs = qs.filter(availability=availability)
    if q:
        qs = qs.filter(title__icontains=q) | qs.filter(sku__icontains=q)

    categories = ProductCategory.objects.all()
    brands = Brand.objects.all()

    return render(request, "website/products_list.html", {
        "site_settings": s,
        "products": qs,
        "categories": categories,
        "brands": brands,
        "selected": {"cat": category, "brand": brand, "avail": availability, "q": q},
    })


def product_detail(request, slug):
    s = get_site_settings()
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, "website/product_detail.html", {
        "site_settings": s,
        "product": product,
    })


# ============================================================
# Blog
# ============================================================

def blog_list(request):
    s = get_site_settings()
    if not s.blog_enabled:
        return redirect("home")

    posts = BlogPost.objects.filter(is_published=True).order_by("-published_at")
    return render(request, "website/blog_list.html", {
        "site_settings": s,
        "posts": posts,
    })


def blog_detail(request, slug):
    s = get_site_settings()
    if not s.blog_enabled:
        return redirect("home")

    post = get_object_or_404(BlogPost, slug=slug, is_published=True)

    prev_post = (
        BlogPost.objects.filter(is_published=True, published_at__lt=post.published_at)
        .order_by("-published_at")
        .first()
    )
    next_post = (
        BlogPost.objects.filter(is_published=True, published_at__gt=post.published_at)
        .order_by("published_at")
        .first()
    )

    related_qs = BlogPost.objects.filter(is_published=True).exclude(id=post.id)
    if getattr(post, "category_id", None):
        related_qs = related_qs.filter(category_id=post.category_id)

    related_posts = related_qs.order_by("-published_at")[:4]

    return render(request, "website/blog_detail.html", {
        "site_settings": s,
        "post": post,
        "prev_post": prev_post,
        "next_post": next_post,
        "related_posts": related_posts,
    })


# ============================================================
# Popup messages (Portal settings)
# ============================================================

@login_required
@require_http_methods(["GET", "POST"])
def popup_messages_settings(request):
    if request.user.role not in ("ADMIN", "MANAGER"):
        return redirect("portal_dashboard")

    qs = PopUpMessage.objects.all().order_by("priority", "-created_at")

    if request.method == "POST":
        form = PopUpMessageForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Mesajul a fost salvat.")
            return redirect("popup_messages_settings")
    else:
        form = PopUpMessageForm()

    return render(request, "portal/popup_messages_settings.html", {
        "messages_qs": qs,
        "form": form,
    })


@login_required
@require_http_methods(["GET", "POST"])
def popup_message_edit(request, pk):
    if request.user.role not in ("ADMIN", "MANAGER"):
        return redirect("portal_dashboard")

    obj = get_object_or_404(PopUpMessage, pk=pk)

    if request.method == "POST":
        form = PopUpMessageForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Mesajul a fost actualizat.")
            return redirect("popup_messages_settings")
    else:
        form = PopUpMessageForm(instance=obj)

    return render(request, "portal/popup_message_edit.html", {
        "form": form,
        "obj": obj,
    })


@login_required
@require_http_methods(["POST"])
def popup_message_delete(request, pk):
    if request.user.role not in ("ADMIN", "MANAGER"):
        return redirect("portal_dashboard")

    obj = get_object_or_404(PopUpMessage, pk=pk)
    obj.delete()
    messages.success(request, "Mesajul a fost șters.")
    return redirect("popup_messages_settings")
