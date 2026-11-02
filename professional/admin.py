from django.contrib import admin

from .models import Experience, Certification, Achievement


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ("role", "organization", "period", "current", "order")
    list_editable = ("current", "order")
    search_fields = ("role", "organization", "description")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {
            "fields": ("role", "organization", "period", "location", "url"),
        }),
        ("Details", {
            "fields": ("description", "current"),
            "description": "Description: one bullet point per line.",
        }),
        ("Display", {"fields": ("order",)}),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ("title", "issuer", "date", "featured", "order")
    list_editable = ("featured", "order")
    search_fields = ("title", "issuer", "credential_id")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {
            "fields": ("title", "issuer", "date", "credential_id", "url"),
        }),
        ("Badge image", {
            "fields": ("image",),
            "description": "Optional. Uploaded to Cloudinary when configured.",
        }),
        ("Display", {"fields": ("featured", "order")}),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ("title", "date", "order")
    list_editable = ("order",)
    search_fields = ("title", "description")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {
            "fields": ("title", "description", "date", "url", "icon"),
            "description": (
                "Icon: a single emoji or short text shown as the marker, "
                "e.g. 🏆, 🥇, ⚡. Leave blank for the default trophy."
            ),
        }),
        ("Display", {"fields": ("order",)}),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
