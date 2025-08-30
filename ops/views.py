from decimal import Decimal
from django.shortcuts import render
from django.http import HttpResponse
from .forms import EstimateForm
from .models import PricingSettings, AddOn, Estimate

def _get_settings():
    # Fetch the single settings row, or defaults if not created yet
    ps = PricingSettings.objects.first()
    if not ps:
        ps = PricingSettings()  # default values from model
    return ps

def _calc_price(service_type: str, frequency: str, hours: Decimal, addon_ids):
    ps = _get_settings()

    # Base hourly rate selection
    if service_type == "residential":
        if frequency == "one_time":
            hourly = Decimal(ps.one_time_res)
        else:
            hourly = Decimal(ps.res_base)
            # Frequency discounts only for residential recurring
            disc = Decimal("0")
            if frequency == "weekly":
                disc = Decimal(ps.weekly_discount or 0) / Decimal("100")
            elif frequency == "biweekly":
                disc = Decimal(ps.biweekly_discount or 0) / Decimal("100")
            elif frequency == "monthly":
                disc = Decimal(ps.monthly_discount or 0) / Decimal("100")
            hourly = hourly * (Decimal("1") - disc)
            # Never below residential floor
            if hourly < Decimal(ps.res_base):
                hourly = Decimal(ps.res_base)
    else:
        # commercial, construction, church – no discounts
        hourly = Decimal(ps.comm_base)

    # Add-ons (flat)
    addons_total = AddOn.objects.filter(id__in=addon_ids).aggregate(
        total_sum=models.Sum("price_flat")
    )["total_sum"] or Decimal("0")

    total = (hourly * Decimal(hours)) + Decimal(addons_total)
    return total.quantize(Decimal("0.01"))

def home(request):
    # Keep a simple homepage
    return HttpResponse("""
    <html>
      <head><title>Cleaning Platform</title></head>
      <body style='font-family:system-ui,Arial,sans-serif;margin:2rem'>
        <h1>Cleaning Platform</h1>
        <p><a href='/estimate/'>Get a free estimate</a></p>
        <p>Admin: <a href='/admin/'>/admin</a></p>
      </body>
    </html>
    """)

def estimate(request):
    result = None
    note = None

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

            if not form.cleaned_data.get("within_radius"):
                note = "You appear to be outside our service area. Our office will contact you. (You can also call 256-736-9944.)"

            result = {
                "price": total,
                "name": est.name,
                "service_type": est.service_type,
                "frequency": est.frequency,
                "hours": est.hours,
                "addons": list(est.addons.values_list("name", flat=True)),
            }
    else:
        form = EstimateForm()

    return render(request, "estimate.html", {"form": form, "result": result, "note": note})
