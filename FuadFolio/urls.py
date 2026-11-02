from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('about/', include('about.urls')),
    path('portfolio/', include('portfolio.urls')),
    path('contact/', include('contact.urls')),

    # New routes — additive, do not change existing ones.
    # The personal "My World" page (games + videos) lives under /myworld/.
    # The professional "Others" page lives under /others/.
    path('others/', include('professional.urls')),
    path('myworld/', include('others.urls')),
    path('chatbot/', include('chatbot.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
