# Generated by Django 3.2.8 on 2022-01-18 22:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20220113_0240'),
    ]

    operations = [
        migrations.AddField(
            model_name='blockchain',
            name='work_threshold',
            field=models.PositiveIntegerField(choices=[(1, 'fffffe0000000000,fffffff000000000,0000000000000000'), (2, 'ffffffc000000000,fffffff800000000,fffffe0000000000')], default=2),
        ),
    ]
