from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

# Create your models here.
class Wallet(models.Model):
    CATEGORY_CHOICES = [
        ('Cash', 'Cash'),
        ('Debit Card', 'Debit Card'),
        ('Credit Card', 'Credit Card'),
        ('Bank Account', 'Bank Account'),
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
                fat.amount -= updated_balance_decimal - initial_balance_decimal

            elif  initial_balance_decimal > updated_balance_decimal:
                # If the updated balance is smaller, increase fat amount
                # fat.amount +=  800
                fat.amount +=  initial_balance_decimal - updated_balance_decimal
           
        else:
            # Compare the balances
            if updated_balance_decimal > initial_balance_decimal:
                # If the updated balance is greater, decrease fat amount
                # fat.amount -= 800
                fat.amount -= updated_balance_decimal - initial_balance_decimal

            else:
                # If the updated balance is smaller, increase fat amount
                # fat.amount +=  800
                fat.amount +=  initial_balance_decimal - updated_balance_decimal
            
        # Save the updated fat instance
        fat.save()

        return fat.amount  # Return the calculated fat amount


class Transaction(models.Model):
    TYPE_CHOICES = [
        ('Income', 'Income'),
        ('Expense', 'Expense'),
    ]

    CATEGORY_CHOICES = [
        ('Food & Drinks', [
            ('Bar, cafe','Bar, cafe'),
            ('Groceries','Groceries'),
            ('Restaurant, fast-food','Restaurant, fast-food'),
        ]),
        ('Shopping', [
            ('Clothes & Shoes','Clothes & Shoes'),
            ('Drug-store, chemist','Drug-store, chemist'),
            ('Restaurant, fast-food','Restaurant, fast-food'),
            ('Electronics, accessories','Electronics, accessories'),
            ('Free time','Free time'),
            ('Gifts, joy','Gifts, joy'),
            ('Stationary, tools','Stationary, tools'),            
        ]),
        ('Housing', [
            ('Energy, utilities','Energy, utilities'),
            ('Maintenance, repairs','Maintenance, repairs'),
            ('Property insurance','Property insurance'),
            ('Rent','Rent'),
            ('Services','Services'),
        ]),
        ('Transportation', [
            ('Business trips','Business trips'),
            ('Long Distance','Long Distance'),
            ('Public transport','Public transport'),
            ('Taxi','Taxi'),
        ]),
        ('Vehicle', [
            ('Fuel', 'Fuel'),
            ('Leasing', 'Leasing'),
            ('Parking', 'Parking'),
            ('Rentals', 'Rentals'),
            ('Vehicle insurance', 'Vehicle insurance'),
            ('Vehicle maintenance', 'Vehicle maintenance'),
            ('Rentals', 'Rentals'),
        ]),
        ('Life & Entertainment', [
            ('Active sport, fitness', 'Active sport, fitness'),
            ('Alcohol, tobacco', 'Alcohol, tobacco'),
            ('Books, audio, subscriptions', 'Books, audio, subscriptions'),
            ('Charity, gifts', 'Charity, gifts'),
            ('Culture, sport events', 'Culture, sport events'),
            ('Education, development', 'Education, development'),
            ('Health care, doctor', 'Health care, doctor'),
            ('Hobbies', 'Hobbies'),
            ('Life Events', 'Life Events'),
            ('Lottery, gambling', 'Lottery, gambling'),
            ('TV, steaming', 'TV, steaming'),
            ('Wellness, beauty', 'Wellness, beauty'),
        ]),
        ('Communication, PC', [
            ('Internet', 'Internet'),
            ('Phone, cell phone', 'Phone, cell phone'),
            ('Postal services', 'Postal services'),
            ('Software, apps, games', 'Software, apps, games'),
           
        ]),
        ('Financial expenses', [
            ('Advisory', 'Advisory'),
            ('Charges, fees', 'Charges, fees'),
            ('Postal services', 'Postal services'),
            ('Child Support', 'Child Support'),
            ('Fines', 'Fines'),
            ('Insurances', 'Insurances'),
            ('Loan, interests', 'Loan, interests'),
            ('Taxes', 'Taxes'),
        ]),

        ('Investments', [
            ('Collections', 'Collections'),
            ('Financial Investments', 'Financial Investments'),
            ('Realty', 'Realty'),
            ('Savings', 'Savings'),
            ('Vehicles, chattels', 'Vehicles, chattels'),
        
        ]),

         ('Income', [
            ('Wage, invoices', 'Wage, invoices'),
            ('Sale', 'Sale'),
            ('Checks, coupons', 'Checks, coupons'),
            ('Child Support', 'Child Support'),
            ('Dues & grants', 'Dues & grants'),
            ('Gifts', 'Gifts'),
            ('Interest, dividents', 'Interest, dividents'),
            ('Lending, renting', 'Lending, renting'),
            ('Lottery, gambling', 'Lottery, gambling'),
            ('Refunds (tax,purchase)', 'Refunds (tax,purchase)'),
            ('Rental Income', 'Rental Income'),
            
            
        
        ]),
        ('Balance Adjustment','Balance Adjustment'),
        ('Other','Other'),

    ]

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    category = models.CharField(max_length=100)  # Main category
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    total_balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))  # New field

    def __str__(self):
        return f"{self.type} - {self.category} - {self.amount}"



class Fat(models.Model):
    wallet = models.OneToOneField(Wallet, on_delete=models.CASCADE, related_name='fat')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Fat for Wallet: {self.wallet.name} - Amount: {self.amount}"
