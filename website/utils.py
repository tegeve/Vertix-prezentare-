from .models import SiteSettings

def get_site_settings():
    """
    Returnează singura instanță de SiteSettings.
    Creează una implicit dacă nu există.
    """
    settings, _ = SiteSettings.objects.get_or_create(pk=1)
    return settings
