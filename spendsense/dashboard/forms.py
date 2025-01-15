from django import forms
from .models import Wallet, Transaction
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from datetime import datetime

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
    )

class TransactionForm(forms.ModelForm):
    
    
    class Meta:
        model = Transaction
        fields = ['wallet', 'type', 'category', 'amount']
        widgets = {
            'wallet': forms.Select(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control', }),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
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



class SignupForm(UserCreationForm):

    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username'
        })
    )   

    email = forms.EmailField(required=True,
        widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your Email'
        }),               
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter Password'
        }),
        
    )
    password2 = forms.CharField(
        label="Confirm Password",
       
        widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirm Password'
        }),
       
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

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

class WalletForm(forms.ModelForm):
    class Meta:
        model = Wallet
        fields = ['name', 'category', 'balance']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'balance': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class WalletTransferForm(forms.Form):
    source_wallet = forms.ModelChoiceField(
        queryset=Wallet.objects.all(),
        label="Source Wallet",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    destination_wallet = forms.ModelChoiceField(
        queryset=Wallet.objects.all(),
        label="Destination Wallet",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        label="Amount",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()
        source_wallet = cleaned_data.get('source_wallet')
        destination_wallet = cleaned_data.get('destination_wallet')
        amount = cleaned_data.get('amount')

        # Check that source and destination wallets are different
        if source_wallet == destination_wallet:
            raise forms.ValidationError("Source and destination wallets must be different.")

        # Check if source wallet has sufficient balance
        if source_wallet and amount and source_wallet.balance < amount:
            raise forms.ValidationError("Insufficient balance in the source wallet.")

        return cleaned_data

class TransactionFilterForm(forms.Form):
    TRANSACTION_TYPES = [
        ('', 'All Types'),  # Default option for no filter
        ('Income', 'Income'),
        ('Expense', 'Expense'),
        ('Transfer', 'Transfer'),
    ]

    type = forms.ChoiceField(
        choices=TRANSACTION_TYPES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Transaction Type"
    )

    category = forms.ChoiceField(
        choices=[('', 'All Categories')],  # Default empty choices
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Category"
    )

    wallet = forms.ModelChoiceField(
        queryset=Wallet.objects.none(),  # Default queryset
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Wallet"
    )

    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        # input_formats=['%d-%m-%Y', '%m-%d-%Y'], 
        label="Start Date",
    )

    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        # input_formats=['%d-%m-%Y', '%m-%d-%Y'],  # Accept both European and ISO formats,
        label="End Date",
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
            self.fields['category'].choices = [('', 'All Categories')] + [(cat, cat) for cat in user_categories]

