# Generated by Django 4.2.1 on 2024-05-16 21:00

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Women',
            fields=[
                ('image_id', models.IntegerField(primary_key=True, serialize=False)),
                ('total', models.FloatField(blank=True)),
                ('subtotal', models.FloatField(blank=True)),
                ('store', models.TextField(blank=True)),
                ('payment_type', models.TextField(blank=True)),
                ('date', models.DateField(blank=True)),
                ('address', models.TextField(blank=True)),
            ],
        ),
    ]