from decimal import Decimal
from math import ceil
from django.shortcuts import render, redirect
from django.db import models
from django.urls import reverse
from .forms import EstimateForm
from .models import PricingSettings, AddOn, Estimate

def _get_settings():
    ps = PricingSettings.objects.first()
    if not ps:
        ps = PricingSettings()
    return ps

def _hours_from_details(ps: PricingSettings, *, bedrooms: int, bathrooms: int, approx_sq_ft: int, levels: int, furnished: bool, pets: bool, cleanliness_level: str, service_type: str) -> Decimal:
    # Base + bedrooms/baths
    hours = Decimal(ps.base_hours_res or 0)
    hours += Decimal(ps.hours_per_bedroom or 0) * Decimal(bedrooms or 0)
    hours += Decimal(ps.hours_per_bathroom or 0) * Decimal(bathrooms or 0)

    # Square footage (per 500 sqft)
    per_500_blocks = ceil((approx_sq_ft or 0) / 500) if approx_sq_ft else 0
    hours += Decimal(ps.hours_per_500_sqft or 0) * Decimal(per_500_blocks)

    # Levels/floors
    hours += Decimal(ps.hours_per_level or 0) * Decimal(levels or 0)

    # Extras
    if pets:
        hours += Decimal(ps.pets_extra_hours or 0)
    if furnished:
        hours += Decimal(ps.furnished_extra_hours or 0)

    # Cleanliness multiplier
    clean_mult = Decimal(ps.cleanliness_multiplier_deep if cleanliness_level == "deep" else ps.cleanliness_multiplier_basic)
    hours *= clean_mult

    # Property multiplier
    prop_map = {
        "residential": ps.property_multiplier_residential,
        "commercial":  ps.property_multiplier_commercial,
        "construction":ps.property_multiplier_construction,
        "move":        ps.property_multiplier_move,
        "church":      ps.property_multiplier_church,
    }
    hours *= Decimal(prop_map.get(service_type, Decimal("1.00")) or 1)

    return hours.quantize(Decimal("0.01"))

def _calc_price(ps: PricingSettings, *, service_type: str, frequency: str, hours: Decimal, addon_ids):
    # Base hourly rate by service type (discounts only on residential recurring)
    if service_type == "residential":
        if frequency == "one_time":
            hourly = Decimal(ps.one_time_res)
        else:
            hourly = Decimal(ps.res_base)
            disc = Decimal("0")
            if frequency == "weekly":
                disc = Decimal(ps.weekly_discount or 0) / Decimal("100")
            elif frequency == "biweekly":
                disc = Decimal(ps.biweekly_discount or 0) / Decimal("100")
            elif frequency == "monthly":
                disc = Decimal(ps.monthly_discount or 0) / Decimal("100")
            hourly = hourly * (Decimal("1") - disc)
            if hourly < Decimal(ps.res_base):
                hourly = Decimal(ps.res_base)
    else:
        hourly = Decimal(ps.comm_base)

    # Add-ons (flat)
    addons_total = AddOn.objects.filter(id__in=addon_ids).aggregate(
        total_sum=models.Sum("price_flat")
    )["total_sum"] or Decimal("0")

    total = (hourly * Decimal(hours)) + Decimal(addons_total)
    return total.quantize(Decimal("0.01"))

def home(request):
    return render(request, "index.html")

def estimate(request):
    if request.method == "POST":
        form = EstimateForm(request.POST)
        if form.is_valid():
            est: Estimate = form.save(commit=False)
            ps = _get_settings()

            computed_hours = _hours_from_details(
                ps,
                bedrooms=est.bedrooms,
                bathrooms=est.bathrooms,
                approx_sq_ft=est.approx_sq_ft,
                levels=est.levels,
                furnished=est.furnished,
                pets=est.pets,
                cleanliness_level=est.cleanliness_level,
                service_type=est.service_type,
            )
            est.hours = computed_hours

            total = _calc_price(
                ps,
                service_type=est.service_type,
                frequency=est.frequency,
                hours=computed_hours,
                addon_ids=[a.id for a in form.cleaned_data.get("addons", [])],
            )
            est.estimated_price = total
            est.save()
            form.save_m2m()

            request.session["last_estimate_price"] = str(total)
            if not form.cleaned_data.get("within_radius"):
                request.session["estimate_note"] = (
                    "You appear to be outside our service area. Our office will contact you. "
                    "(You can also call 256-736-9944.)"
                )
            else:
                request.session.pop("estimate_note", None)

            return redirect(reverse("estimate_thanks"))
    else:
        form = EstimateForm()

    return render(request, "estimate.html", {"form": form})

def estimate_thanks(request):
    price = request.session.pop("last_estimate_price", None)
    note = request.session.pop("estimate_note", None)
    return render(request, "estimate_thanks.html", {"price": price, "note": note})
