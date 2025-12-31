from .models import SiteSettings

def get_site_settings():
    obj = SiteSettings.objects.first()
    if not obj:
        obj = SiteSettings.objects.create()
    return obj
