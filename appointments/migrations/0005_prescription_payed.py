# Generated by Django 4.2 on 2024-12-06 12:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0004_prescription'),
    ]

    operations = [
        migrations.AddField(
            model_name='prescription',
            name='payed',
            field=models.BooleanField(default=False),
        ),
    ]
