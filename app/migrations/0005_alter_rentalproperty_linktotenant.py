# Generated by Django 4.2.3 on 2023-07-21 01:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0004_rentalproperty"),
    ]

    operations = [
        migrations.AlterField(
            model_name="rentalproperty",
            name="linkToTenant",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="app.tenant",
            ),
        ),
    ]