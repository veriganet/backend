# Generated by Django 3.2.8 on 2021-11-11 16:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='created_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
