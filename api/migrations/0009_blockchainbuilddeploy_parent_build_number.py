# Generated by Django 3.2.8 on 2021-11-25 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_auto_20211123_2054'),
    ]

    operations = [
        migrations.AddField(
            model_name='blockchainbuilddeploy',
            name='parent_build_number',
            field=models.IntegerField(default=0, null=True),
        ),
    ]
