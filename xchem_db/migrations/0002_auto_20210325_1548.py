# Generated by Django 3.1.7 on 2021-03-25 15:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xchem_db', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sourcewell',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='sourcewell',
            name='deactivation_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]