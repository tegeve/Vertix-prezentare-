from django.urls import path
from . import views, views_chat

urlpatterns = [
    # ============================================================
    # Dashboard
    # ============================================================
    path("", views.dashboard, name="portal_dashboard"),
    path("", views.dashboard, name="portal_home"),  # alias (evită NoReverseMatch dacă ai folosit portal_home)

    # ============================================================
    # Tickets
    # ============================================================
    path("ticket/creare/", views.ticket_create, name="ticket_create"),
    path("ticket/<int:pk>/assign/", views.ticket_assign, name="ticket_assign"),
    path("ticket/<int:pk>/status/", views.ticket_update_status, name="ticket_update_status"),

    path("tickets/<int:pk>/edit/", views.ticket_edit, name="ticket_edit"),
    path("tickets/<int:pk>/delete/", views.ticket_delete, name="ticket_delete"),

    # ============================================================
    # Public requests
    # ============================================================
    path("public-requests/<int:pk>/edit/", views.public_request_edit, name="public_request_edit"),
    path("public-requests/<int:pk>/delete/", views.public_request_delete, name="public_request_delete"),

    path(
        "public-request-attachments/<int:pk>/delete/",
        views.public_request_attachment_delete,
        name="public_request_attachment_delete",
    ),

    # ============================================================
    # Site settings
    # ============================================================
    path("setari-site/", views.site_settings_view, name="portal_site_settings"),

    # ============================================================
    # Inline create (pentru tab-uri din dashboard)
    # ============================================================
    path("status/create-inline/", views.status_create_inline, name="status_create_inline"),
    path("technician/create-inline/", views.technician_create_inline, name="technician_create_inline"),

    # ============================================================
    # Statusuri CRUD (pagini separate)
    # ============================================================
    path("statusuri/", views.status_list, name="status_list"),
    path("statusuri/adauga/", views.status_create, name="status_create"),
    path("statusuri/<int:pk>/edit/", views.status_update, name="status_update"),
    path("statusuri/<int:pk>/sterge/", views.status_delete, name="status_delete"),

    # ============================================================
    # Tehnicieni CRUD (pagini separate)
    # ============================================================
    path("tehnicieni/", views.tech_list, name="tech_list"),
    path("tehnicieni/adauga/", views.tech_create, name="tech_create"),
    path("tehnicieni/<int:pk>/edit/", views.tech_update, name="tech_update"),
    path("tehnicieni/<int:pk>/sterge/", views.tech_delete, name="tech_delete"),

    # ============================================================
    # Export
    # ============================================================
    path("portal/export.xlsx", views.portal_export_xlsx, name="portal_export_xlsx"),

    # ============================================================
    # Chat (generic: Ticket / PublicRequest)
    # IMPORTANT: am scos rutele vechi ticket_chat / ticket_chat_post
    # deoarece acum folosești GenericForeignKey.
    # ============================================================
    path("chat/unread-count/", views_chat.chat_unread_count, name="chat_unread_count"),
    path("chat/<str:kind>/<int:object_id>/post/", views_chat.chat_post, name="chat_post"),
    path("chat/autocomplete/users/", views_chat.chat_user_autocomplete, name="chat_user_autocomplete"),

]
