# Generated by Django 3.2.8 on 2022-05-15 01:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=512)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=64)),
                ('message', models.CharField(max_length=2048)),
            ],
            options={
                'ordering': ['id'],
            },
        ),
    ]
