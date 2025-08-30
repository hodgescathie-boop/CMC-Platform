from django.db import models
from decimal import Decimal

class PricingSettings(models.Model):
    # Floors & rates (USD per hour)
    res_base = models.DecimalField(max_digits=6, decimal_places=2, default=125)      # Residential floor
    one_time_res = models.DecimalField(max_digits=6, decimal_places=2, default=200)  # One-time residential
    comm_base = models.DecimalField(max_digits=6, decimal_places=2, default=185)     # Commercial/Construction/Church floor

    # Frequency discounts (residential only), in percent
    weekly_discount = models.DecimalField(max_digits=5, decimal_places=2, default=15)
    biweekly_discount = models.DecimalField(max_digits=5, decimal_places=2, default=10)
    monthly_discount = models.DecimalField(max_digits=5, decimal_places=2, default=5)

    # Service area
    service_radius_miles = models.PositiveIntegerField(default=30)
    service_zip_center = models.CharField(max_length=10, default="35055")

    # --- Hour estimate knobs (admin can tune for any business) ---
    base_hours_res = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("2.00"))
    hours_per_bedroom = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.50"))
    hours_per_bathroom = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.50"))
    hours_per_500_sqft = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.25"))
    hours_per_level = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.25"))
    pets_extra_hours = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.25"))
    furnished_extra_hours = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.25"))

    # Cleanliness multipliers
    cleanliness_multiplier_basic = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("1.00"))
    cleanliness_multiplier_deep = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("1.50"))

    # Property type multipliers
    property_multiplier_residential = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("1.00"))
    property_multiplier_commercial  = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("1.20"))
    property_multiplier_construction= models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("1.60"))
    property_multiplier_move        = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("1.40"))
    property_multiplier_church      = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("1.30"))

    def __str__(self):
        return "Pricing Settings"

    class Meta:
        verbose_name = "Pricing settings"
        verbose_name_plural = "Pricing settings"


class AddOn(models.Model):
    key = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    price_flat = models.DecimalField(max_digits=6, decimal_places=2, default=50)  # $50 each by default

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Add on"
        verbose_name_plural = "Add ons"


class Estimate(models.Model):
    SERVICE_CHOICES = [
        ("residential", "Residential"),
        ("commercial", "Commercial"),
        ("construction", "Construction cleanup"),
        ("move", "Move in / Move out"),
        ("church", "Church"),
    ]
    CLEAN_CHOICES = [
        ("basic", "Basic (bathrooms, light dust, floors, wipe surfaces)"),
        ("deep", "Deep (floor to ceiling; add-ons separate)"),
    ]
    FREQ_CHOICES = [
        ("one_time", "One-time"),
        ("weekly", "Weekly"),
        ("biweekly", "Bi-weekly"),
        ("monthly", "Monthly"),
    ]

    # Customer info
    name = models.CharField(max_length=120)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    address = models.CharField(max_length=255, blank=True)
    zip_code = models.CharField(max_length=10, blank=True)

    # Service selection
    within_radius = models.BooleanField(default=True, help_text="Customer is within 30 miles of 35055")
    service_type = models.CharField(max_length=20, choices=SERVICE_CHOICES)
    cleanliness_level = models.CharField(max_length=20, choices=CLEAN_CHOICES, default="basic")
    frequency = models.CharField(max_length=20, choices=FREQ_CHOICES)

    # Home/space details
    furnished = models.BooleanField(default=True)
    pets = models.BooleanField(default=False)
    approx_sq_ft = models.PositiveIntegerField(default=1500)
    bedrooms = models.PositiveIntegerField(default=2)
    bathrooms = models.PositiveIntegerField(default=2)
    levels = models.PositiveIntegerField(default=1)

    # Auto-computed hours (stored for record)
    hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Auto-computed from details")

    # Add-ons & result
    addons = models.ManyToManyField(AddOn, blank=True)
    estimated_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} – {self.service_type} ({self.frequency})"

    class Meta:
        verbose_name = "Estimate"
        verbose_name_plural = "Estimates"
