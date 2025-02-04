# Generated by Django 5.1.4 on 2025-02-01 15:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0008_alter_transaction_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='charity_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='charity_percentage',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Percentage allocated for charity (e.g., 10 for 10%)', max_digits=5, null=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='investment_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='investment_percentage',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Percentage allocated for investment (e.g., 10 for 10%)', max_digits=5, null=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='savings_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='savings_percentage',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Percentage allocated for savings (e.g., 10 for 10%)', max_digits=5, null=True),
        ),
        migrations.AlterField(
            model_name='wallet',
            name='category',
            field=models.CharField(choices=[('Cash', 'Cash'), ('Debit Card', 'Debit Card'), ('Credit Card', 'Credit Card'), ('Bank Account', 'Bank Account'), ('Savings', 'Savings'), ('Investment', 'Investment'), ('General', 'General')], max_length=50),
        ),
    ]
