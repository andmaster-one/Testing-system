# Generated by Django 3.1.2 on 2020-10-26 07:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('testing', '0003_auto_20201023_1702'),
    ]

    operations = [
        migrations.AlterField(
            model_name='savesessionauthusers',
            name='session_data',
            field=models.TextField(blank=True),
        ),
    ]
