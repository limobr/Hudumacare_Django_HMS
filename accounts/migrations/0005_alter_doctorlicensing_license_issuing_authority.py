# Generated by Django 4.2 on 2024-12-02 05:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_doctoreducation_completion_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctorlicensing',
            name='license_issuing_authority',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
