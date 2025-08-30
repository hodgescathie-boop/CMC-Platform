from django.db import models

class PricingSettings(models.Model):
    # Floors & rates (USD per hour)
    res_base = models.DecimalField(max_digits=6, decimal_places=2, default=125)   # Residential floor
    one_time_res = models.DecimalField(max_digits=6, decimal_places=2, default=200)  # One-time residential
    comm_base = models.DecimalField(max_digits=6, decimal_places=2, default=185)  # Commercial/Construction/Church floor

    # Frequency discounts (residential only), in percent
    weekly_discount = models.DecimalField(max_digits=5, decimal_places=2, default=15)    # 15% default
    biweekly_discount = models.DecimalField(max_digits=5, decimal_places=2, default=10)  # 10% default
    monthly_discount = models.DecimalField(max_digits=5, decimal_places=2, default=5)    # 5% default

    # Service area
    service_radius_miles = models.PositiveIntegerField(default=30)
    service_zip_center = models.CharField(max_length=10, default="35055")

    def __str__(self):
        return "Pricing Settings"


class AddOn(models.Model):
    key = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    price_flat = models.DecimalField(max_digits=6, decimal_places=2, default=50)  # $50 each by default

    def __str__(self):
        return self.name


class Estimate(models.Model):
    SERVICE_CHOICES = [
        ("residential", "Residential"),
        ("commercial", "Commercial"),
        ("construction", "Construction"),
        ("church", "Church"),
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
    frequency = models.CharField(max_length=20, choices=FREQ_CHOICES)

    # Time input for now (team labor hours)
    hours = models.DecimalField(max_digits=5, decimal_places=2, help_text="Estimated team labor hours")

    # Add-ons
    addons = models.ManyToManyField(AddOn, blank=True)

    # Result
    estimated_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} – {self.service_type} ({self.frequency})"
