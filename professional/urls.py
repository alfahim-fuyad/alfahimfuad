from django.urls import path

from . import views

# The url_name is `others` because the page is labelled "Others" in the
# navbar. The professional app is mounted at /others/ in the project
# urls.py.
urlpatterns = [
    path("", views.others, name="others"),
]
