# Generated by Django 4.2.3 on 2023-07-22 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0008_remove_propertyphoto_property_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="rentalproperty",
            name="city",
            field=models.TextField(
                choices=[
                    ("Oxford", "Oxford"),
                    ("Pontotoc", "Pontotoc"),
                    ("New Albany", "New Albany"),
                ],
                null=True,
            ),
        ),
    ]