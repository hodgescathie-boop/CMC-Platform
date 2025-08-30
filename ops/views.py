from decimal import Decimal
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

def _calc_price(service_type: str, frequency: str, hours: Decimal, addon_ids):
    ps = _get_settings()

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
            total = _calc_price(
                service_type=form.cleaned_data["service_type"],
                frequency=form.cleaned_data["frequency"],
                hours=form.cleaned_data["hours"],
                addon_ids=[a.id for a in form.cleaned_data.get("addons", [])],
            )
            est.estimated_price = total
            est.save()
            form.save_m2m()

            # stash price in session just to show on the thanks page (simple & stateless)
            request.session["last_estimate_price"] = str(total)

            # note about service radius — in v2 we can email/notify office as needed
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
    ctx = {"price": price, "note": note}
    return render(request, "estimate_thanks.html", ctx)
