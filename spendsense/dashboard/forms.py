from django import forms
from .models import Wallet, Transaction
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from datetime import datetime
from decimal import Decimal
from django.utils.translation import gettext_lazy as _

class NumberInputWithCommas(forms.TextInput):
    def format_value(self, value):
        if value is not None:
            try:
                return "{:,}".format(Decimal(value))  # Format with commas
            except ValueError:
                return value
        return ''

# done translation
class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        label=_("Username"),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter your username')
        })
    )
    password = forms.CharField(
        label =_("Password"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter your password')
        })
    )

class WalletChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        """Translate the wallet name before displaying it."""
        return _(obj.name)  # This will translate the wallet name to Greek if a translation exists


# done translation
class TransactionForm(forms.ModelForm):
    
    
    wallet = WalletChoiceField(
        queryset=Wallet.objects.none(), 
        empty_label="---------",  # "Select a wallet"
        widget=forms.Select(attrs={'class': 'form-control custom-wallet-class'}) , # Add CSS class here\
        label=_("Select Wallet")

    )

    # Additional fields for income transactions
    savings_percentage = forms.DecimalField(
        required=False,
        label=_("Savings Percentage"),
        widget=forms.NumberInput(attrs={
            'class': 'form-control income-field',
            'placeholder': _('Enter savings %'),
            # 'style': 'display:none;'
        })
    )
    investment_percentage = forms.DecimalField(
        required=False,
        label=_("Investment Percentage"),
        widget=forms.NumberInput(attrs={
            'class': 'form-control income-field',
            'placeholder': _('Enter investment %'),
            # 'style': 'display:none;'
        })
    )
    charity_percentage = forms.DecimalField(
        required=False,
        label=_("Charity Percentage"),
        widget=forms.NumberInput(attrs={
            'class': 'form-control income-field',
            'placeholder': _('Enter charity %'),
            # 'style': 'display:none;'
        })
    )

    class Meta:
        model = Transaction
        fields = ['wallet', 'type', 'savings_percentage',
                  'investment_percentage','charity_percentage',
                  'category', 'amount', 'description'
                ]
       
        
        widgets = {
        
            'type': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control', }),
            'amount': NumberInputWithCommas(attrs={
                'class': 'form-control form-number',
                'min': '0.00',  # Optional: Enforce minimum value
                'max': '9999999999999.99',  # Allow large numbers
                'step': '0.01',  # Allow decimal inputs                
            }),
            'description': forms.Textarea(attrs={  # Added widget for description
                'class': 'form-control',
                'rows': 4,  # Adjust the height of the text box
                'placeholder': _('Add a description (optional)...'),
            }),
        }

        # Add custom labels
        labels = {
            'wallet': _('Select Wallet'),
            'type': _('Transaction Type'),
            'category': _('Category'),
            'amount': _('Transaction Amount'),
            'description': _('Description'),  # Added label for description
        }




    def __init__(self, *args, **kwargs):
        # Extract 'user' from kwargs if present
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)  # Call the parent class's __init__
        if user:
            # Filter the queryset for wallets to only include the logged-in user's wallets
            self.fields['wallet'].queryset = Wallet.objects.filter(user=user)
        else:
            # Default to an empty queryset if no user is provided
            self.fields['wallet'].queryset = Wallet.objects.none()


    def clean(self):
        """
        If the transaction is an income, calculate the amounts for savings,
        investment, and charity based on the percentages and the income amount.
        """
        cleaned_data = super().clean()
        transaction_type = cleaned_data.get("type")
        amount = cleaned_data.get("amount")
        if transaction_type == "Income" and amount is not None:
            # Get percentages; default to 0 if not provided.
            savings_pct = cleaned_data.get("savings_percentage") or 0
            investment_pct = cleaned_data.get("investment_percentage") or 0
            charity_pct = cleaned_data.get("charity_percentage") or 0
            wallet = cleaned_data.get('wallet')
            # Calculate the respective amounts.
            cleaned_data["savings_amount"] = amount * savings_pct / 100
            cleaned_data["investment_amount"] = amount * investment_pct / 100
            cleaned_data["charity_amount"] = amount * charity_pct / 100

            # Optionally, you might want to enforce that the percentages do not exceed 100%
            # or that the sum of percentages does not exceed 100.
            total_pct = savings_pct + investment_pct + charity_pct
            if total_pct > 100:
                raise forms.ValidationError(
                    _("The total percentage allocation cannot exceed 100%.")
                )
            # If a predefined wallet is selected, disallow a percentage for that same wallet
            if wallet and wallet.is_predefined:
                if wallet.name.lower() == 'savings' and savings_pct != Decimal('0'):
                    raise ValidationError(_("You cannot add a savings percentage when the Savings wallet is selected."))
                if wallet.name.lower() == 'investment' and investment_pct != Decimal('0'):
                    raise ValidationError(_("You cannot add an investment percentage when the Investment wallet is selected."))
                if wallet.name.lower() == 'charity' and charity_pct != Decimal('0'):
                    raise ValidationError(_("You cannot add a charity percentage when the Charity wallet is selected."))


        return cleaned_data


# done translation
class SignupForm(UserCreationForm):

     # New fields for name and surname
    first_name = forms.CharField(
        label=_("First Name:"),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter your first name')
        }),
        required=True  # Mark as required or False as needed
    )
    
    last_name = forms.CharField(
        label=_("Last Name:"),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter your last name')
        }),
        required=True
    )



    username = forms.CharField(
        label=_("Username:"),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter your username')
        })
    )   

    email = forms.EmailField(required=True,
        label=_("Email:"),
        widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': _('Enter your Email')
        }),               
    )
    password1 = forms.CharField(
        label=_("Password:"),
        widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': _('Enter Password')
        }),
        
    )
    password2 = forms.CharField(
        label=_("Confirm Password:"),
       
        widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': _('Confirm Password')
        }),
       
    )

    class Meta:
        model = User
        fields = ['first_name','last_name','username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already registered.")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        return password2

# done translation
class WalletForm(forms.ModelForm):
    class Meta:
        model = Wallet
        fields = ['name', 'category', 'balance']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'balance': NumberInputWithCommas(attrs={
                'class': 'form-control form-number',
                'min': '0.00',  # Optional: Enforce minimum value
                'max': '9999999999999.99',  # Allow large numbers
                'step': '0.01',  # Allow decimal inputs
                
                
            }),
        }

        # Add custom labels
        labels = {
            'name': _('Wallet Name'),
            'category': _('Category'),
            'balance': _('Balance'),
        }

    
# done translation
class WalletTransferForm(forms.Form):
    source_wallet = WalletChoiceField(
        queryset=Wallet.objects.none(), 
        empty_label="---------",  # "Select a wallet"
        widget=forms.Select(attrs={'class': 'form-control custom-wallet-class'}) , # Add CSS class here\
        label=_("Source Wallet")

    )

    destination_wallet = WalletChoiceField(
        queryset=Wallet.objects.none(), 
        empty_label="---------",  # "Select a wallet"
        widget=forms.Select(attrs={'class': 'form-control custom-wallet-class'}) , # Add CSS class here\
        label=_("Destination Wallet")

    )

    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        label=_("Amount"),
        widget=NumberInputWithCommas(attrs={
                'class': 'form-control form-number',
                'min': '0.00',  # Optional: Enforce minimum value
                'max': '9999999999999.99',  # Allow large numbers
                'step': '0.01',  # Allow decimal inputs
                
                
            }),
    )

    use_fat_amount = forms.BooleanField(
        required=False,
        label=_("Recover Negative Balance Correction"),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input','id':'id_use_fat_amount'}),
    )

    fat_wallet = forms.ModelChoiceField(
        queryset= Wallet.objects.none(),
        label=_("Choose Wallet"),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control field-fat_wallet d-none'}),  # Initially hidden
    )

    def clean(self):
        cleaned_data = super().clean()
        source_wallet = cleaned_data.get('source_wallet')
        destination_wallet = cleaned_data.get('destination_wallet')
        amount = cleaned_data.get('amount')
        use_fat_amount = cleaned_data.get('use_fat_amount')
        fat_wallet = cleaned_data.get('fat_wallet')

        # Check that source and destination wallets are different
        if source_wallet == destination_wallet:
            raise forms.ValidationError("Source and destination wallets must be different.")

        # Check if source wallet has sufficient balance
        if source_wallet and amount and source_wallet.balance < amount:
            raise forms.ValidationError("Insufficient balance in the source wallet.")

         # If "Use Fat Amount" is checked, validate the fat wallet
        if use_fat_amount:
            if not fat_wallet:
                raise forms.ValidationError("Please select a wallet with a fat amount.")
            if fat_wallet.fat.amount > amount:
                raise forms.ValidationError("The selected fat wallet does not have enough fat amount.")

        return cleaned_data
    

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Extract the user from the kwargs
        super().__init__(*args, **kwargs)
        if user:
            # Filter wallets based on the current user
            self.fields['source_wallet'].queryset = Wallet.objects.filter(user=user)
            self.fields['destination_wallet'].queryset = Wallet.objects.filter(user=user)
            # Filter `fat_wallet` for the current user with the specified condition
            self.fields['fat_wallet'].queryset = Wallet.objects.filter(
                user=user,  # Adjust `owner` to your actual field linking Wallet to User
                fat__amount__lt=Decimal('0.00')  # Additional condition
            )

# done translation 
class TransactionFilterForm(forms.Form):
    TRANSACTION_TYPES = [
        ('', _('All Types')),  # Default option for no filter
        ('Income', _('Income')),
        ('Expense', _('Expense')),
        ('Transfer', _('Transfer')),
    ]

    type = forms.ChoiceField(
        choices=TRANSACTION_TYPES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label=_("Transaction Type")
    )

    category = forms.ChoiceField(
        choices=[('All Categories', _('All Categories'))],  # Default empty choices
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label=_("Category")
    )

    wallet = WalletChoiceField(
        queryset=Wallet.objects.none(), 
        empty_label="---------",  # "Select a wallet"
        widget=forms.Select(attrs={'class': 'form-control custom-wallet-class'}) , # Add CSS class here\
        label=_("Choose Wallet")

    )

    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        # input_formats=['%d-%m-%Y', '%m-%d-%Y'], 
        label=_("Start Date"),
    )

    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        # input_formats=['%d-%m-%Y', '%m-%d-%Y'],  # Accept both European and ISO formats,
        label=_("End Date"),
    )


    def __init__(self, *args, **kwargs):
        # Extract the user from kwargs
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Dynamically filter wallets for the user
        if self.user:
            self.fields['wallet'].queryset = Wallet.objects.filter(user=self.user)

           # Dynamically filter categories for transactions belonging to the user's wallets
            user_categories = Transaction.objects.filter(wallet__user=self.user).values_list('category', flat=True).distinct()
            self.fields['category'].choices = [('', _('All Categories'))] + [(cat, _(cat)) for cat in user_categories]

