# Generated by Django 4.1.5 on 2023-03-24 06:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0019_orders_amountpaid'),
    ]

    operations = [
        migrations.AddField(
            model_name='orders',
            name='oid',
            field=models.CharField(default='', max_length=255),
        ),
    ]
