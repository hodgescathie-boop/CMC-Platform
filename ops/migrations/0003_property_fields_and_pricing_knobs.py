from django.db import migrations, models
from decimal import Decimal

class Migration(migrations.Migration):

    dependencies = [
        ("ops", "0002_auto_inputs_and_knobs"),
    ]

    operations = [
        # Estimate fields
        migrations.AddField(
            model_name="estimate",
            name="cleanliness_level",
            field=models.CharField(choices=[("basic", "Basic (bathrooms, light dust, floors, wipe surfaces)"), ("deep", "Deep (floor to ceiling; add-ons separate)")], default="basic", max_length=20),
        ),
        migrations.AddField(
            model_name="estimate",
            name="furnished",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="estimate",
            name="pets",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="estimate",
            name="approx_sq_ft",
            field=models.PositiveIntegerField(default=1500),
        ),
        migrations.AddField(
            model_name="estimate",
            name="levels",
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name="estimate",
            name="service_type",
            field=models.CharField(choices=[("residential", "Residential"), ("commercial", "Commercial"), ("construction", "Construction cleanup"), ("move", "Move in / Move out"), ("church", "Church")], max_length=20),
        ),

        # PricingSettings knobs
        migrations.AddField(
            model_name="pricingsettings",
            name="hours_per_500_sqft",
            field=models.DecimalField(decimal_places=2, default=Decimal("0.25"), max_digits=5),
        ),
        migrations.AddField(
            model_name="pricingsettings",
            name="hours_per_level",
            field=models.DecimalField(decimal_places=2, default=Decimal("0.25"), max_digits=5),
        ),
        migrations.AddField(
            model_name="pricingsettings",
            name="pets_extra_hours",
            field=models.DecimalField(decimal_places=2, default=Decimal("0.25"), max_digits=5),
        ),
        migrations.AddField(
            model_name="pricingsettings",
            name="furnished_extra_hours",
            field=models.DecimalField(decimal_places=2, default=Decimal("0.25"), max_digits=5),
        ),
        migrations.AddField(
            model_name="pricingsettings",
            name="cleanliness_multiplier_basic",
            field=models.DecimalField(decimal_places=2, default=Decimal("1.00"), max_digits=5),
        ),
        migrations.AddField(
            model_name="pricingsettings",
            name="cleanliness_multiplier_deep",
            field=models.DecimalField(decimal_places=2, default=Decimal("1.50"), max_digits=5),
        ),
        migrations.AddField(
            model_name="pricingsettings",
            name="property_multiplier_residential",
            field=models.DecimalField(decimal_places=2, default=Decimal("1.00"), max_digits=5),
        ),
        migrations.AddField(
            model_name="pricingsettings",
            name="property_multiplier_commercial",
            field=models.DecimalField(decimal_places=2, default=Decimal("1.20"), max_digits=5),
        ),
        migrations.AddField(
            model_name="pricingsettings",
            name="property_multiplier_construction",
            field=models.DecimalField(decimal_places=2, default=Decimal("1.60"), max_digits=5),
        ),
        migrations.AddField(
            model_name="pricingsettings",
            name="property_multiplier_move",
            field=models.DecimalField(decimal_places=2, default=Decimal("1.40"), max_digits=5),
        ),
        migrations.AddField(
            model_name="pricingsettings",
            name="property_multiplier_church",
            field=models.DecimalField(decimal_places=2, default=Decimal("1.30"), max_digits=5),
        ),
    ]
