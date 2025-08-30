from django.db import migrations, models
from decimal import Decimal

class Migration(migrations.Migration):

    dependencies = [
        ('ops', '0001_initial'),
    ]

    operations = [
        # Add estimate inputs
        migrations.AddField(
            model_name='estimate',
            name='bathrooms',
            field=models.PositiveIntegerField(default=2),
        ),
        migrations.AddField(
            model_name='estimate',
            name='bedrooms',
            field=models.PositiveIntegerField(default=2),
        ),
        migrations.AlterField(
            model_name='estimate',
            name='hours',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=5,
                null=True,
                help_text='Auto-computed from bedrooms/bathrooms'
            ),
        ),

        # Add pricing knobs
        migrations.AddField(
            model_name='pricingsettings',
            name='base_hours_res',
            field=models.DecimalField(decimal_places=2, default=Decimal('2.00'), max_digits=5),
        ),
        migrations.AddField(
            model_name='pricingsettings',
            name='hours_per_bathroom',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.50'), max_digits=5),
        ),
        migrations.AddField(
            model_name='pricingsettings',
            name='hours_per_bedroom',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.50'), max_digits=5),
        ),
    ]

