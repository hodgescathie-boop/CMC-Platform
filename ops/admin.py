from django.contrib import admin
from .models import PricingSettings, AddOn, Estimate

@admin.register(PricingSettings)
class PricingSettingsAdmin(admin.ModelAdmin):
    list_display = ("res_base", "one_time_res", "comm_base",
                    "weekly_discount", "biweekly_discount", "monthly_discount",
                    "service_radius_miles", "service_zip_center")

@admin.register(AddOn)
class AddOnAdmin(admin.ModelAdmin):
    list_display = ("name", "price_flat", "key")
    search_fields = ("name", "key")

@admin.register(Estimate)
class EstimateAdmin(admin.ModelAdmin):
    list_display = ("name", "service_type", "frequency", "hours", "estimated_price", "created_at")
    list_filter = ("service_type", "frequency", "created_at")
    search_fields = ("name", "email", "phone", "zip_code")
    filter_horizontal = ("addons",)
