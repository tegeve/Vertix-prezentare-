from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.urls import path, include
from django.views.generic import RedirectView
from website.admin_site import vertix_admin_site

urlpatterns = [
    path("", RedirectView.as_view(url="/ro/", permanent=False)),  # <-- ADĂUGAT
    path("i18n/", include("django.conf.urls.i18n")),
]

urlpatterns += i18n_patterns(
    path("admin/", vertix_admin_site.urls),
    path("cont/", include("accounts.urls")),
    path("portal/", include("portal.urls")),
    path("", include("website.urls")),
    path("portal/documente/", include("documents.urls", namespace="documents")),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
