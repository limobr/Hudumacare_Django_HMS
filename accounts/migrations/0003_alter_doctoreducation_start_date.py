# Generated by Django 4.2 on 2024-12-02 05:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_userprofile_date_of_birth_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctoreducation',
            name='start_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]