from django.urls import path

from . import views

urlpatterns = [
    # The page label is "My World" — the URL slug is `myworld` so it
    # doesn't collide with the new professional "Others" page mounted
    # at /others/ by the `professional` app.
    path("", views.my_world, name="myworld"),
]
