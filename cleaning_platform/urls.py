from django.contrib import admin
from django.urls import path
from ops.views import home, estimate, estimate_thanks

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("estimate/", estimate, name="estimate"),
    path("estimate/thanks/", estimate_thanks, name="estimate_thanks"),
]
