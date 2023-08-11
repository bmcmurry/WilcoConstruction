# Generated by Django 4.2.3 on 2023-08-09 01:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0016_constructionticket_slug_rentalproperty_slug_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="tenant",
            name="currentBalance",
        ),
        migrations.RemoveField(
            model_name="tenant",
            name="linkToProperty",
        ),
        migrations.CreateModel(
            name="Lease",
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
                ("slug", models.SlugField(blank=True, null=True)),
                ("pricePerMonth", models.FloatField(verbose_name="Price")),
                ("dateCreated", models.DateTimeField(auto_now_add=True)),
                (
                    "currentBalance",
                    models.IntegerField(default=0, verbose_name="Balance"),
                ),
                (
                    "linkToProperty",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="app.rentalproperty",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="tenant",
            name="linkToLease",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="app.lease",
            ),
        ),
    ]