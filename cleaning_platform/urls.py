from django.contrib import admin
from django.urls import path
from ops.views import home, estimate

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("estimate/", estimate, name="estimate"),
]
