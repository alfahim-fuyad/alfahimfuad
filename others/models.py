"""
Models for the "Others" page.

Two admin-editable content types live here:

* ``Game``      — a personal mini-game the visitor can play inline.
                  The game itself is an embeddable URL (itch.io, an HTML5
                  build hosted anywhere, or a self-contained data: URL) shown
                  inside an iframe on the Others page.

* ``VideoLink`` — an external video (YouTube, Vimeo, or any embeddable URL)
                  shown as a thumbnail card that opens an embedded player.

Both models are admin-managed (add / edit / delete / reorder) and use
Cloudinary for their preview image when Cloudinary is configured in
settings; otherwise they fall back to local media storage.
"""

from django.db import models


def _game_image_path(instance, filename):
    return f"others/games/{instance.slug or filename}"


def _video_image_path(instance, filename):
    return f"others/videos/{instance.slug or filename}"


class Game(models.Model):
    title = models.CharField(max_length=160)
    slug = models.SlugField(
        max_length=160, blank=True,
        help_text="Optional URL slug. Used only for organising uploaded images.",
    )
    description = models.TextField(
        blank=True,
        help_text="Short description shown under the game title.",
    )
    embed_url = models.URLField(
        max_length=500,
        help_text=(
            "URL of the playable game. Can be an itch.io embed URL, an "
            "HTML5 build hosted anywhere, or any URL that can be loaded in "
            "an <iframe>."
        ),
    )
    image = models.ImageField(
        upload_to=_game_image_path, blank=True, null=True,
        help_text="Preview / cover image (uploaded to Cloudinary when configured).",
    )
    play_label = models.CharField(
        max_length=40, blank=True, default="Play Now",
        help_text="Text on the play button.",
    )
    featured = models.BooleanField(
        default=False,
        help_text="Featured games are shown first.",
    )
    order = models.PositiveIntegerField(
        default=0, help_text="Lower numbers show first.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-featured", "order", "-id"]
        verbose_name = "Personal game"
        verbose_name_plural = "Personal games"

    def __str__(self):
        return self.title


class VideoLink(models.Model):
    title = models.CharField(max_length=160)
    slug = models.SlugField(
        max_length=160, blank=True,
        help_text="Optional URL slug. Used only for organising uploaded images.",
    )
    description = models.TextField(
        blank=True,
        help_text="Short description shown under the video title.",
    )
    video_url = models.URLField(
        max_length=500,
        help_text=(
            "Watch URL of the video. YouTube watch URLs "
            "(https://www.youtube.com/watch?v=ID) and youtu.be/ID URLs are "
            "auto-converted into embeddable URLs. Vimeo and direct embed "
            "URLs are also supported."
        ),
    )
    thumbnail = models.ImageField(
        upload_to=_video_image_path, blank=True, null=True,
        help_text=(
            "Optional custom thumbnail. If left blank, a YouTube thumbnail "
            "is auto-derived from the video URL when possible."
        ),
    )
    duration = models.CharField(
        max_length=20, blank=True,
        help_text="Optional, e.g. '12:34'.",
    )
    featured = models.BooleanField(
        default=False,
        help_text="Featured videos are shown first.",
    )
    order = models.PositiveIntegerField(
        default=0, help_text="Lower numbers show first.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-featured", "order", "-id"]
        verbose_name = "Video link"
        verbose_name_plural = "Video links"

    def __str__(self):
        return self.title
