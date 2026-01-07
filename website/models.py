from django.db import models
from django.urls import reverse

class Industry(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    short = models.CharField(max_length=260, blank=True)
    
    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Service(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)

    short = models.CharField(max_length=260, blank=True)
    description = models.TextField(blank=True)

    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text="Ex: bi bi-gear, bi bi-robot, bi bi-wrench"
    )

    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("service_detail", args=[self.slug])

class Project(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    industry = models.ForeignKey(Industry, on_delete=models.SET_NULL, null=True, blank=True)
    summary = models.CharField(max_length=280, blank=True)
    description = models.TextField(blank=True)
    cover = models.ImageField(upload_to="projects/", blank=True, null=True)
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("project_detail", args=[self.slug])


class Post(models.Model):
    title = models.CharField(max_length=220)
    slug = models.SlugField(unique=True)
    excerpt = models.CharField(max_length=300, blank=True)
    content = models.TextField()
    cover = models.ImageField(upload_to="blog/", blank=True, null=True)
    published_at = models.DateTimeField()

    class Meta:
        ordering = ["-published_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("blog_detail", args=[self.slug])


class Job(models.Model):
    title = models.CharField(max_length=220)
    slug = models.SlugField(unique=True)
    location = models.CharField(max_length=200, blank=True)
    description = models.TextField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class ContactMessage(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    company = models.CharField(max_length=120, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    is_read = models.BooleanField(default=False)  # ✅ NOU

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.email}"


class SiteSettings(models.Model):
    # Pagini publice (toggle)
    home_enabled = models.BooleanField(default=True)
    about_enabled = models.BooleanField(default=True)
    services_enabled = models.BooleanField(default=True)
    projects_enabled = models.BooleanField(default=True)
    industries_enabled = models.BooleanField(default=True)
    contact_enabled = models.BooleanField(default=True)
    blog_enabled = models.BooleanField(default=True)
    careers_enabled = models.BooleanField(default=True)
    gdpr_enabled = models.BooleanField(default=True)
    cookies_enabled = models.BooleanField(default=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return "Site Settings"

# models.py
from django.db import models
from django.utils.text import slugify

class ProductCategory(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=120, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    AVAILABILITY_CHOICES = [
        ("IN_STOCK", "În stoc"),
        ("ORDER", "La comandă"),
        ("LEAD_TIME", "Lead time"),
        ("OUT", "Indisponibil"),
    ]

    title = models.CharField(max_length=180)
    slug = models.SlugField(unique=True, blank=True)
    sku = models.CharField(max_length=64, blank=True)  # cod produs
    brand = models.ForeignKey(Brand, null=True, blank=True, on_delete=models.SET_NULL)
    category = models.ForeignKey(ProductCategory, null=True, blank=True, on_delete=models.SET_NULL)

    short_description = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)

    # specificații simple B2B
    specs = models.JSONField(default=dict, blank=True)  # ex: {"Tensiune":"24V", "Putere":"2kW"}

    availability = models.CharField(max_length=20, choices=AVAILABILITY_CHOICES, default="ORDER")
    lead_time_days = models.PositiveIntegerField(null=True, blank=True)  # dacă e cazul
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    datasheet = models.FileField(upload_to="datasheets/", null=True, blank=True)
    image = models.ImageField(upload_to="products/", null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["order", "title"]

    def __str__(self):
        return self.title


class AboutPage(models.Model):
    # HERO
    hero_title = models.CharField(max_length=200, default="Construim soluții digitale care cresc afaceri")
    hero_subtitle = models.CharField(max_length=300, blank=True, default="Suntem Vertix – partenerul tău în dezvoltare software, automatizări și soluții digitale moderne.")
    hero_image = models.ImageField(upload_to="about/", blank=True, null=True)

    # POVESTE
    story_title = models.CharField(max_length=120, default="Povestea noastră")
    story_text = models.TextField(blank=True)
    story_image = models.ImageField(upload_to="about/", blank=True, null=True)

    # MISIUNE / VIZIUNE / VALORI
    mission_title = models.CharField(max_length=80, default="Misiune")
    mission_text = models.TextField(blank=True)
    mission_image = models.ImageField(upload_to="about/", blank=True, null=True)

    vision_title = models.CharField(max_length=80, default="Viziune")
    vision_text = models.TextField(blank=True)
    vision_image = models.ImageField(upload_to="about/", blank=True, null=True)

    values_title = models.CharField(max_length=80, default="Valori")
    values_text = models.TextField(blank=True, help_text="Folosește linii separate, una pe rând (ex: Transparență)")
    values_image = models.ImageField(upload_to="about/", blank=True, null=True)

    # DIFERENȚIATORI
    differentiators_title = models.CharField(max_length=120, default="Ce ne diferențiază")
    differentiators_text = models.TextField(blank=True, help_text="Folosește linii separate, una pe rând")
    differentiators_image = models.ImageField(upload_to="about/", blank=True, null=True)

    # CTA
    cta_title = models.CharField(max_length=160, default="Ai un proiect sau o idee?")
    cta_text = models.CharField(max_length=240, blank=True, default="Hai să discutăm și să găsim varianta potrivită pentru tine.")
    cta_button_text = models.CharField(max_length=40, default="Contactează-ne")
    cta_button_url = models.CharField(max_length=200, default="/contact/")
    cta_image = models.ImageField(upload_to="about/", blank=True, null=True)

    # Ton (corporate / prietenos / premium) – ca să avem un control simplu
    TONE_CHOICES = [
        ("CORPORATE", "Corporate"),
        ("FRIENDLY", "Prietenos"),
        ("PREMIUM", "Premium"),
    ]
    tone = models.CharField(max_length=10, choices=TONE_CHOICES, default="FRIENDLY")

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "About Page"
        verbose_name_plural = "About Page"

    def __str__(self):
        return "About Page (single)"


from django.db import models
from django.utils import timezone

class PopUpMessage(models.Model):
    STYLE_INFO = "INFO"
    STYLE_SUCCESS = "SUCCESS"
    STYLE_WARNING = "WARNING"
    STYLE_DANGER = "DANGER"
    STYLE_CHOICES = [
        (STYLE_INFO, "Info"),
        (STYLE_SUCCESS, "Success"),
        (STYLE_WARNING, "Warning"),
        (STYLE_DANGER, "Danger"),
    ]

    title = models.CharField(max_length=120)
    body = models.TextField()
    style = models.CharField(max_length=10, choices=STYLE_CHOICES, default=STYLE_INFO)

    # Perioada de activitate
    start_at = models.DateTimeField(null=True, blank=True)
    end_at = models.DateTimeField(null=True, blank=True)

    is_enabled = models.BooleanField(default=True)

    # Predefinite / template
    is_preset = models.BooleanField(default=False)
    preset_key = models.CharField(max_length=60, blank=True)  # ex: "HOLIDAYS_CLOSED"

    # Comportament
    show_once_per_browser = models.BooleanField(default=True)  # via localStorage
    show_on_home_only = models.BooleanField(default=False)

    priority = models.PositiveIntegerField(default=100)  # mai mic = mai “sus”
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["priority", "-created_at"]

    def __str__(self):
        return self.title

    def is_active_now(self):
        if not self.is_enabled:
            return False
        now = timezone.now()
        if self.start_at and now < self.start_at:
            return False
        if self.end_at and now > self.end_at:
            return False
        return True


class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    short = models.CharField(max_length=300, blank=True)
    content = models.TextField()  # va conține HTML din editor

    image = models.ImageField(upload_to="blog/covers/", blank=True, null=True)  # cover
    published_at = models.DateTimeField(default=timezone.now)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["-published_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("blog_detail", args=[self.slug])


class BlogPostImage(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name="gallery")
    image = models.ImageField(upload_to="blog/gallery/")
    caption = models.CharField(max_length=200, blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return self.caption or f"Image for {self.post.title}"

