# Generated by Django 5.1.4 on 2025-01-28 18:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0005_transaction_description_alter_transaction_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='wallet',
            name='is_predefined',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='wallet',
            name='category',
            field=models.CharField(choices=[('Cash', 'Cash'), ('Debit Card', 'Debit Card'), ('Credit Card', 'Credit Card'), ('Bank Account', 'Bank Account'), ('Savings', 'Savings'), ('Investment', 'Investmentls'), ('General', 'General')], max_length=50),
        ),
    ]
