from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from django.utils.translation import gettext_lazy as _
# Create your models here.

# done translation
class Wallet(models.Model):
    CATEGORY_CHOICES = [
        ('Cash', _('Cash')),
        ('Debit Card', _('Debit Card')),
        ('Credit Card', _('Credit Card')),
        ('Bank Account', _('Bank Account')),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wallets')
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.name

    def initialize_fat(self, initial_balance):
        # Get or create the 'Fat' instance
        fat, created = Fat.objects.get_or_create(wallet=self)
        if created:
            fat.amount = initial_balance
            fat.save()

    def update_fat_balance(self, initial_balance):
        """
        Updates the corresponding Fat instance's amount based on the wallet's balance.
        """
        # Get or create the 'Fat' instance
        fat, created = Fat.objects.get_or_create(wallet=self)
        # fat_amount = Decimal(fat.amount)
        # Convert both balances to Decimal for precision
        updated_balance_decimal = Decimal(str(self.balance))  # Ensure correct precision with strings
        initial_balance_decimal = Decimal(str(initial_balance))  # Convert wallet's balance to Decimal
       
        
        if created:
           
            # If the Fat instance was just created, initialize its amount
              # If the Fat instance was newly created, initialize its amount to 0.00

            fat.amount = Decimal(0.00)
        

             # Compare the balances
            # Compare the balances
            if initial_balance_decimal < updated_balance_decimal:
                # If the updated balance is greater, decrease fat amount
                # fat.amount -= 800
                fat.amount += updated_balance_decimal - initial_balance_decimal

            elif  initial_balance_decimal > updated_balance_decimal:
                # If the updated balance is smaller, increase fat amount
                # fat.amount +=  800
                fat.amount -=  initial_balance_decimal - updated_balance_decimal
           
        else:
            # Compare the balances
            if updated_balance_decimal > initial_balance_decimal:
                # If the updated balance is greater, decrease fat amount
                # fat.amount -= 800
                fat.amount += updated_balance_decimal - initial_balance_decimal

            else:
                # If the updated balance is smaller, increase fat amount
                # fat.amount +=  800
                fat.amount -=  initial_balance_decimal - updated_balance_decimal
            
        # Save the updated fat instance
        fat.save()

        return fat.amount  # Return the calculated fat amount

# done translation
class Transaction(models.Model):
    TYPE_CHOICES = [
        ('Income', _('Income')),
        ('Expense', _('Expense')),
    ]

    CATEGORY_CHOICES = [
        (_('Food & Drinks'), [
            ('Bar, cafe',_('Bar, cafe')),
            ('Groceries',_('Groceries')),
            ('Restaurant, fast-food',_('Restaurant, fast-food')),
        ]),
        (_('Shopping'), [
            ('Clothes & Shoes',_('Clothes & Shoes')),
            ('Drug-store, chemist',_('Drug-store, chemist')),
            ('Restaurant, fast-food',_('Restaurant, fast-food')),
            ('Electronics, accessories',_('Electronics, accessories')),
            ('Free time',_('Free time')),
            ('Gifts, joy',_('Gifts, joy')),
            ('Stationary, tools',_('Stationary, tools')),            
        ]),
        (_('Housing'), [
            ('Energy, utilities',_('Energy, utilities')),
            ('Maintenance, repairs',_('Maintenance, repairs')),
            ('Property insurance',_('Property insurance')),
            ('Rent',_('Rent')),
            ('Services',_('Services')),
        ]),
        (_('Transportation'), [
            ('Business trips',_('Business trips')),
            ('Long Distance',_('Long Distance')),
            ('Public transport',_('Public transport')),
            ('Taxi',_('Taxi')),
        ]),
        (_('Vehicle'), [
            ('Fuel', _('Fuel')),
            ('Leasing', _('Leasing')),
            ('Parking', _('Parking')),
            ('Rentals', _('Rentals')),
            ('Vehicle insurance', _('Vehicle insurance')),
            ('Vehicle maintenance', _('Vehicle maintenance')),
            ('Rentals', _('Rentals')),
        ]),
        (_('Life & Entertainment'), [
            ('Active sport, fitness', _('Active sport, fitness')),
            ('Alcohol, tobacco', _('Alcohol, tobacco')),
            ('Books, audio, subscriptions', _('Books, audio, subscriptions')),
            ('Charity, gifts', _('Charity, gifts')),
            ('Culture, sport events', _('Culture, sport events')),
            ('Education, development', _('Education, development')),
            ('Health care, doctor', _('Health care, doctor')),
            ('Hobbies', _('Hobbies')),
            ('Life Events', _('Life Events')),
            ('Lottery, gambling', _('Lottery, gambling')),
            ('TV, steaming', _('TV, steaming')),
            ('Wellness, beauty', _('Wellness, beauty')),
        ]),
        (_('Communication, PC'), [
            ('Internet', _('Internet')),
            ('Phone, cell phone', _('Phone, cell phone')),
            ('Postal services', _('Postal services')),
            ('Software, apps, games', _('Software, apps, games')),
           
        ]),
        (_('Financial expenses'), [
            ('Advisory', _('Advisory')),
            ('Charges, fees', _('Charges, fees')),
            ('Postal services', _('Postal services')),
            ('Child Support', _('Child Support')),
            ('Fines', _('Fines')),
            ('Insurances', _('Insurances')),
            ('Loan, interests', _('Loan, interests')),
            ('Taxes', _('Taxes')),
        ]),

        (_('Investments'), [
            ('Collections', _('Collections')),
            ('Financial Investments', _('Financial Investments')),
            ('Realty', _('Realty')),
            ('Savings', _('Savings')),
            ('Vehicles, chattels', _('Vehicles, chattels')),
        
        ]),

         (_('Income'), [
            ('Wage, invoices', _('Wage, invoices')),
            ('Sale', _('Sale')),
            ('Checks, coupons', _('Checks, coupons')),
            ('Child Support', _('Child Support')),
            ('Dues & grants', _('Dues & grants')),
            ('Gifts', _('Gifts')),
            ('Interest, dividents', _('Interest, dividents')),
            ('Lending, renting', _('Lending, renting')),
            ('Lottery, gambling', _('Lottery, gambling')),
            ('Refunds (tax,purchase)', _('Refunds (tax,purchase)')),
            ('Rental Income', _('Rental Income')),
            
            
        
        ]),
        ('Other',_('Other')),

    ]

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    category = models.CharField(max_length=100,choices=CATEGORY_CHOICES)  # Main category
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    total_balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))  # New field
    description = models.TextField(blank=True, null=True)  # New field for text input
    def __str__(self):
        return f"{self.type} - {self.category} - {self.amount}"



class Fat(models.Model):
    wallet = models.OneToOneField(Wallet, on_delete=models.CASCADE, related_name='fat')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Fat for Wallet: {self.wallet.name} - Amount: {self.amount}"
