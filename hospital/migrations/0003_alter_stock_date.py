# Generated by Django 5.2.1 on 2025-05-25 09:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hospital', '0002_stock_stock_value'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stock',
            name='date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
