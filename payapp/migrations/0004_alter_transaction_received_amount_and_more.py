# Generated by Django 4.2.11 on 2024-05-08 21:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payapp', '0003_remove_transaction_amount_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='received_amount',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='sent_amount',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]