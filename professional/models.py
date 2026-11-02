"""
Models for the "Others" (professional) page.

The page is the user's professional showcase — work experience,
certifications, and achievements. Each model is fully admin-editable
(add / edit / delete / reorder) and uses Cloudinary for any uploaded
image (certification badge, achievement logo) when Cloudinary is
configured; otherwise it falls back to local media storage.

The site owner's professional summary, skills, core competencies,
languages, and interests continue to live on the existing
`home.Profile` row — the `professional` view pulls those in directly
instead of duplicating them here.
"""

from django.db import models


class Experience(models.Model):
    role = models.CharField(max_length=160)
    organization = models.CharField(max_length=160, blank=True)
    period = models.CharField(
        max_length=80, blank=True,
        help_text="e.g. 'Jan 2024 – Present' or '2023 – 2024'.",
    )
    location = models.CharField(max_length=120, blank=True)
    description = models.TextField(
        blank=True,
        help_text=(
            "One bullet point per line. Each line is rendered as a "
            "list item inside the experience card."
        ),
    )
    current = models.BooleanField(
        default=False,
        help_text="Tick to highlight this as the current role.",
    )
    url = models.URLField(
        blank=True,
        help_text="Optional link to the company / project page.",
    )
    order = models.PositiveIntegerField(
        default=0, help_text="Lower numbers show first.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "-id"]
        verbose_name = "Work experience"
        verbose_name_plural = "Work experience"

    def __str__(self):
        if self.organization:
            return f"{self.role} — {self.organization}"
        return self.role


class Certification(models.Model):
    title = models.CharField(max_length=200)
    issuer = models.CharField(
        max_length=160, blank=True,
        help_text="Organisation that issued the certificate.",
    )
    date = models.CharField(
        max_length=60, blank=True,
        help_text="e.g. 'March 2024'. Free text.",
    )
    credential_id = models.CharField(
        max_length=120, blank=True,
        help_text="Optional credential / license ID.",
    )
    url = models.URLField(
        blank=True,
        help_text="Optional link to verify the certificate.",
    )
    image = models.ImageField(
        upload_to="professional/certs/", blank=True, null=True,
        help_text="Optional badge / logo image (uploaded to Cloudinary when configured).",
    )
    featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(
        default=0, help_text="Lower numbers show first.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-featured", "order", "-id"]
        verbose_name = "Certification"
        verbose_name_plural = "Certifications"

    def __str__(self):
        if self.issuer:
            return f"{self.title} — {self.issuer}"
        return self.title


class Achievement(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(
        blank=True,
        help_text="One or two sentences describing the achievement.",
    )
    date = models.CharField(
        max_length=60, blank=True,
        help_text="e.g. '2024' or 'Oct 2023'. Free text.",
    )
    url = models.URLField(
        blank=True,
        help_text="Optional link to a blog post, article, or proof.",
    )
    icon = models.CharField(
        max_length=8, blank=True,
        help_text=(
            "Optional single emoji or short text shown as the icon, "
            "e.g. '🏆', '🥇', '⚡'. Leave blank for the default icon."
        ),
    )
    order = models.PositiveIntegerField(
        default=0, help_text="Lower numbers show first.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "-id"]
        verbose_name = "Achievement"
        verbose_name_plural = "Achievements"

    def __str__(self):
        return self.title
