from dashboard.models import Wallet

# Define the predefined wallet names and categories
predefined_wallets = [
    {'name': 'Savings', 'category': 'Savings'},
    {'name': 'Investment', 'category': 'Investment'},
    {'name': 'Charity', 'category': 'General'},
]

# Loop through predefined wallet definitions
for wallet_data in predefined_wallets:
    # Check if a wallet exists with the specified name and category
    wallets_to_update = Wallet.objects.filter(
        name=wallet_data['name'],
        category=wallet_data['category'],
        is_predefined=False  # Ensure we only update non-predefined wallets
    )

    # Update the wallets to mark them as predefined
    for wallet in wallets_to_update:
        wallet.is_predefined = True
        wallet.save()
        print(f"Marked wallet '{wallet.name}' as predefined.")

# Mark all other wallets as not predefined
Wallet.objects.filter(is_predefined=False).update(is_predefined=False)
print("All other wallets are marked as user-created.")
