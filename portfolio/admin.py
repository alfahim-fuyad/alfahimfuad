from django.contrib import admin
from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "project_url",
        "has_image",
        "image_preview",
    )
    search_fields = ("title", "description")
    readonly_fields = ("image_preview",)

    fieldsets = (
        (None, {
            "fields": ("title", "description", "project_url"),
        }),
        ("Project image", {
            "fields": ("image", "image_preview"),
            "description": (
                "Upload, replace, or clear the project image here. "
                "If the project title exactly matches a GitHub repo "
                "name, this image overrides the placeholder thumbnail "
                "shown on the Projects page. To delete the image "
                "entirely, tick the 'Clear' checkbox next to it and "
                "save. When Cloudinary is configured, uploads go "
                "straight to Cloudinary."
            ),
        }),
    )

    @admin.display(boolean=True, description="Has image")
    def has_image(self, obj):
        return bool(obj.image)

    @admin.display(description="Preview")
    def image_preview(self, obj):
        if not obj or not obj.image:
            return "(no image uploaded)"
        from django.utils.html import format_html
        return format_html(
            '<img src="{}" style="max-height:160px; border-radius:8px; '
            'border:1px solid #ccc;" alt="preview">',
            obj.image.url,
        )
