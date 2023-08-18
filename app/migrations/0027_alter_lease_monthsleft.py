# Generated by Django 4.2.3 on 2023-08-18 02:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0026_alter_lease_monthsleft"),
    ]

    operations = [
        migrations.AlterField(
            model_name="lease",
            name="monthsLeft",
            field=models.IntegerField(
                default=0, verbose_name="Months Remaining on Lease"
            ),
        ),
    ]
