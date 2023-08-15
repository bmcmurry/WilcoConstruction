# Generated by Django 4.2.3 on 2023-08-15 01:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0018_tenantpayment_linked_lease_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="ConstructionJob",
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
                ("title", models.CharField(max_length=50)),
                (
                    "isFeaturedConstruction",
                    models.BooleanField(
                        default=False, verbose_name="Featured Construction"
                    ),
                ),
                ("dateCreated", models.DateField(auto_now_add=True)),
                ("isComplete", models.BooleanField(default=False)),
                ("description", models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name="ConstructionJobPhoto",
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
                    "constructionOfImage",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="app.constructionjob",
                    ),
                ),
            ],
        ),
        migrations.RemoveField(
            model_name="constructionticketphoto",
            name="ConstructionOfImage",
        ),
        migrations.AlterField(
            model_name="tenant",
            name="linkToLease",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="app.lease",
            ),
        ),
        migrations.AlterField(
            model_name="tenantpayment",
            name="app_user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="app.tenant"
            ),
        ),
        migrations.DeleteModel(
            name="ConstructionTicket",
        ),
        migrations.DeleteModel(
            name="ConstructionTicketPhoto",
        ),
    ]