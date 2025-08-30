# Generated manually to run on Heroku (slug is read-only for makemigrations)
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AddOn',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.SlugField(max_length=50, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('price_flat', models.DecimalField(decimal_places=2, default=50, max_digits=6)),
            ],
        ),
        migrations.CreateModel(
            name='PricingSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('res_base', models.DecimalField(decimal_places=2, default=125, max_digits=6)),
                ('one_time_res', models.DecimalField(decimal_places=2, default=200, max_digits=6)),
                ('comm_base', models.DecimalField(decimal_places=2, default=185, max_digits=6)),
                ('weekly_discount', models.DecimalField(decimal_places=2, default=15, max_digits=5)),
                ('biweekly_discount', models.DecimalField(decimal_places=2, default=10, max_digits=5)),
                ('monthly_discount', models.DecimalField(decimal_places=2, default=5, max_digits=5)),
                ('service_radius_miles', models.PositiveIntegerField(default=30)),
                ('service_zip_center', models.CharField(default='35055', max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Estimate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('phone', models.CharField(blank=True, max_length=40)),
                ('address', models.CharField(blank=True, max_length=255)),
                ('zip_code', models.CharField(blank=True, max_length=10)),
                ('within_radius', models.BooleanField(default=True, help_text='Customer is within 30 miles of 35055')),
                ('service_type', models.CharField(choices=[('residential', 'Residential'), ('commercial', 'Commercial'), ('construction', 'Construction'), ('church', 'Church')], max_length=20)),
                ('frequency', models.CharField(choices=[('one_time', 'One-time'), ('weekly', 'Weekly'), ('biweekly', 'Bi-weekly'), ('monthly', 'Monthly')], max_length=20)),
                ('hours', models.DecimalField(decimal_places=2, help_text='Estimated team labor hours', max_digits=5)),
                ('estimated_price', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='estimate',
            name='addons',
            field=models.ManyToManyField(blank=True, to='ops.addon'),
        ),
    ]
