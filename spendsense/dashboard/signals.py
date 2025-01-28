from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Wallet
from decimal import Decimal
from django.utils.translation import gettext_lazy as _

@receiver(post_save, sender=User)
def create_or_update_default_wallets(sender, instance, created, **kwargs):
    predefined_wallets = [
        {'name': 'Savings', 'category': 'Savings'},
        {'name': 'Investment', 'category': 'Investment'},
        {'name': 'Charity', 'category': 'General'},
    ]

    for wallet_data in predefined_wallets:
        wallet, wallet_created = Wallet.objects.get_or_create(
            user=instance,
            name=wallet_data['name'],
            defaults={
                'category': wallet_data['category'],
                'balance': Decimal('0.00'),
                'is_predefined': True,  # Mark as predefined
            },
        )
        if wallet_created:
            wallet.initialize_fat(Decimal('0.00'))
