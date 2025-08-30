# ops/models.py
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models


# ---------- Utilities ----------

USD = Decimal("0.01")


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# ---------- Domain Models ----------

class AddOn(TimeStampedModel):
    class PriceType(models.TextChoices):
        FLAT = "flat", "Flat amount"
        HOURLY = "hourly", "Per hour"

    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    price_type = models.CharField(
        max_length=10,
        choices=PriceType.choices,
        default=PriceType.FLAT,
    )
    amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="If 'Per hour', this amount is multiplied by hours.",
    )
    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        unit = "/hr" if self.price_type == self.PriceType.HOURLY else ""
        return f"{self.name} (${self.amount}{unit})"

    class Meta:
        ordering = ["name"]
        verbose_name = "Add-on"
        verbose_name_plural = "Add ons"


class PricingSettings(TimeStampedModel):
    """
    Global pricing configuration. Typically one row that the app reads.
    """
    hourly_rate = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Base hourly rate for labor.",
    )
    min_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("2.0"),
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Minimum billable hours for any estimate.",
    )
    outside_radius_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Applied when the job is outside the default service radius.",
    )
    service_radius_miles = models.PositiveIntegerField(
        default=30,
        help_text="Default service radius in miles.",
    )
    base_zip = models.CharField(
        max_length=10,
        default="35055",
        validators=[RegexValidator(r"^\d{5}(-\d{4})?$", "Enter a valid ZIP code.")],
        help_text="Home base ZIP code for radius checks.",
    )

    def __str__(self) -> str:
        return "Pricing settings"

    class Meta:
        verbose_name = "Pricing settings"
        verbose_name_plural = "Pricing settings"
        ordering = ["-created_at"]


class Estimate(TimeStampedModel):
    class ServiceType(models.TextChoices):
        STANDARD = "standard", "Standard clean"
        DEEP = "deep", "Deep clean"
        MOVE = "move_in_out", "Move in / Move out"
        OFFICE = "office", "Office / Commercial"

    class Frequency(models.TextChoices):
        ONE_TIME = "one_time", "One-time"
        WEEKLY = "weekly", "Weekly"
        BIWEEKLY = "biweekly", "Every 2 weeks"
        MONTHLY = "monthly", "Monthly"

    # Customer & location
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    address = models.CharField(max_length=255)
    zip_code = models.CharField(
        max_length=10,
        validators=[RegexValidator(r"^\d{5}(-\d{4})?$", "Enter a valid ZIP code.")],
    )

    # Job details
    service_type = models.CharField(
        max_length=20,
        choices=ServiceType.choices,
        default=ServiceType.STANDARD,
    )
    frequency = models.CharField(
        max_length=20,
        choices=Frequency.choices,
        default=Frequency.ONE_TIME,
    )
    hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Estimated labor hours (before minimums).",
    )
    addons = models.ManyToManyField(AddOn, blank=True)
    within_radius = models.BooleanField(
        default=True,
        help_text="If unchecked, an outside-radius fee may apply.",
    )
    notes = models.TextField(blank=True)

    # Quoting lifecycle
    class Status(models.TextChoices):
        NEW = "new", "New"
        QUOTED = "quoted", "Quoted"
        SCHEDULED = "scheduled", "Scheduled"
        COMPLETED = "completed", "Completed"
        CANCELED = "canceled", "Canceled"

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        db_index=True,
    )
    quoted_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Stored snapshot of the price at time of quote.",
    )

    def __str__(self) -> str:
        return f"Estimate #{self.pk or '—'} — {self.name}"

    # -------- Pricing helpers (for upcoming auto-calculation) --------

    def _get_pricing(self, pricing: PricingSettings | None = None) -> PricingSettings:
        pricing = pricing or PricingSettings.objects.order_by("-created_at").first()
        if not pricing:
            # Safe default if settings not yet created
            return PricingSettings(
                hourly_rate=Decimal("0.00"),
                min_hours=Decimal("0.00"),
                outside_radius_fee=Decimal("0.00"),
                service_radius_miles=30,
                base_zip="35055",
            )
        return pricing

    def calculate_quote(self, pricing: PricingSettings | None = None) -> Decimal:
        """
        Calculate a quote using current PricingSettings and selected AddOns.
        This does not persist the value; call save_quote() to store it.
        """
        pricing = self._get_pricing(pricing)

        billable_hours = max(Decimal(self.hours or 0), pricing.min_hours)
        total = billable_hours * pricing.hourly_rate

        for addon in self.addons.all():
            if addon.price_type == AddOn.PriceType.HOURLY:
                total += billable_hours * addon.amount
            else:
                total += addon.amount

        if not self.within_radius:
            total += pricing.outside_radius_fee

        # Round to cents using bankers' rounding behavior aligned with typical invoices
        return total.quantize(USD, rounding=ROUND_HALF_UP)

    def save_quote(self, pricing: PricingSettings | None = None, commit: bool = True) -> Decimal:
        """
        Compute and store the quoted_total. Returns the computed value.
        """
        quote = self.calculate_quote(pricing=pricing)
        self.quoted_total = quote
        if commit:
            self.save(update_fields=["quoted_total", "updated_at"])
        return quote

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Estimate"
        verbose_name_plural = "Estimates"
