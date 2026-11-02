from django.contrib import admin

from .models import Game, VideoLink


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ("title", "featured", "order", "embed_url")
    list_editable = ("featured", "order")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {
            "fields": ("title", "slug", "description", "embed_url", "play_label"),
        }),
        ("Preview image", {
            "fields": ("image",),
            "description": "Uploaded to Cloudinary when CLOUDINARY_URL is set.",
        }),
        ("Display", {
            "fields": ("featured", "order"),
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )


@admin.register(VideoLink)
class VideoLinkAdmin(admin.ModelAdmin):
    list_display = ("title", "featured", "order", "video_url")
    list_editable = ("featured", "order")
    search_fields = ("title", "description", "video_url")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {
            "fields": ("title", "slug", "description", "video_url", "duration"),
        }),
        ("Thumbnail", {
            "fields": ("thumbnail",),
            "description": (
                "Optional. If blank, a YouTube thumbnail is auto-derived "
                "from the video URL when possible."
            ),
        }),
        ("Display", {
            "fields": ("featured", "order"),
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
