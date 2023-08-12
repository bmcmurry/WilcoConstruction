# Generated by Django 4.2.3 on 2023-08-12 16:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0017_remove_tenant_currentbalance_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="tenantpayment",
            name="linked_lease",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="app.lease",
            ),
        ),
        migrations.AddField(
            model_name="tenantpayment",
            name="payment_amount",
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name="lease",
            name="currentBalance",
            field=models.FloatField(default=0, verbose_name="Balance"),
        ),
        migrations.AlterField(
            model_name="lease",
            name="pricePerMonth",
            field=models.FloatField(default=0, verbose_name="Price"),
        ),
    ]
