# Generated by Django 4.2.5 on 2024-07-14 09:53

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("inventory", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="customer",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("email", models.EmailField(max_length=254)),
                ("name", models.CharField(max_length=100)),
                ("phone", models.CharField(max_length=20)),
                ("street", models.CharField(max_length=255)),
                ("city", models.CharField(max_length=100)),
                ("state", models.CharField(max_length=100)),
                ("zip", models.CharField(max_length=20)),
                ("country", models.CharField(max_length=100)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AlterField(
            model_name="productinventory",
            name="sale_price",
            field=models.DecimalField(
                decimal_places=2,
                error_messages={
                    "name": {"max_length": "the price must be between 0 and 999.99."}
                },
                help_text="format: maximum price 999.99",
                max_digits=10,
                verbose_name="sale price",
            ),
        ),
    ]