from django.db import models
from django.conf import settings

class PageView(models.Model):
    path = models.CharField(max_length=400, db_index=True)
    method = models.CharField(max_length=10, blank=True)
    visitor_id = models.UUIDField(null=True, blank=True, db_index=True)
    status_code = models.PositiveSmallIntegerField(null=True, blank=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="page_views"
    )

    ua = models.CharField(max_length=300, blank=True)
    referer = models.CharField(max_length=400, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.path} @ {self.created_at:%Y-%m-%d %H:%M}"
