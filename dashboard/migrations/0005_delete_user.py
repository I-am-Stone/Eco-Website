# Generated by Django 5.1rc1 on 2024-09-03 13:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0004_user_alter_order_customer_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='User',
        ),
    ]
