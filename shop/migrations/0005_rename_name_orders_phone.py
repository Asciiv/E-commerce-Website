# Generated by Django 4.1.5 on 2023-03-02 17:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0004_orders'),
    ]

    operations = [
        migrations.RenameField(
            model_name='orders',
            old_name='name',
            new_name='phone',
        ),
    ]
