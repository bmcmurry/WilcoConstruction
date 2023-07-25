# Generated by Django 4.2.3 on 2023-07-22 16:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0005_alter_rentalproperty_linktotenant"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="rentalproperty",
            name="linkToTenant",
        ),
        migrations.RemoveField(
            model_name="rentalproperty",
            name="picture",
        ),
        migrations.AddField(
            model_name="tenant",
            name="linkToProperty",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="app.rentalproperty",
            ),
        ),
        migrations.CreateModel(
            name="PropertyPhoto",
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
                ("picture", models.ImageField(upload_to="images/")),
                (
                    "property",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="app.propertyphoto",
                    ),
                ),
            ],
        ),
    ]