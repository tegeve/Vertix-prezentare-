from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("despre-noi/", views.about, name="about"),
    path("servicii/", views.services_list, name="services_list"),
    path("servicii/<slug:slug>/", views.service_detail, name="service_detail"),

    path("proiecte/", views.projects_list, name="projects_list"),
    path("proiecte/<slug:slug>/", views.project_detail, name="project_detail"),

    path("industrii/", views.industries, name="industries"),

    path("contact/", views.contact, name="contact"),

    path("blog/", views.blog_list, name="blog_list"),
    path("blog/<slug:slug>/", views.blog_detail, name="blog_detail"),

    path("cariere/", views.careers, name="careers"),
    path("gdpr/", views.gdpr, name="gdpr"),
    path("cookies/", views.cookies, name="cookies"),

    path("produse/", views.products_list, name="products_list"),
    path("produse/<slug:slug>/", views.product_detail, name="product_detail"),

    path("about/", views.about, name="about"),

    path("portal/settings/popups/", views.popup_messages_settings, name="popup_messages_settings"),
    path("portal/settings/popups/<int:pk>/edit/", views.popup_message_edit, name="popup_message_edit"),
    path("portal/settings/popups/<int:pk>/delete/", views.popup_message_delete, name="popup_message_delete"),

]
