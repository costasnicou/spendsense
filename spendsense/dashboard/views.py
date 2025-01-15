
# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Wallet, Transaction
from .forms import WalletForm, TransactionForm
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django.contrib.auth.views import LoginView
from .forms import CustomLoginForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Transaction, Wallet, Fat
from .forms import TransactionForm, SignupForm,TransactionFilterForm,WalletTransferForm
from django.contrib import messages
from django.contrib.auth import login
from decimal import Decimal
from datetime import datetime
from django.utils import timezone
from django.urls import reverse
from django.http import JsonResponse




class CustomLoginView(LoginView):
    authentication_form = CustomLoginForm
    def get_success_url(self):
        # Redirect to the dashboard with the logged-in user's username
        return reverse('dashboard', kwargs={'user': self.request.user.username})


def homepage(request):
    return render(request, 'dashboard/homepage.html')


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the user to the database
            return redirect('login')  # Redirect to your desired page
    else:
        form = SignupForm()

    return render(request, 'dashboard/signup.html', {'form': form})


@login_required
def dashboard(request,user):

    # Ensure the logged-in user matches the user in the URL
    if request.user.username != user:
        return render(request, "403.html", status=403)

    if request.method == 'POST':
        
        if 'submit_wallet_form' in request.POST:
            wallet_form_submitted = WalletForm(request.POST)
            if wallet_form_submitted.is_valid():
                
                wallet = wallet_form_submitted.save(commit=False)
               
                wallet.user = request.user
                wallet.save()
                wallet.initialize_fat(Decimal(0.00))
                return redirect('dashboard')
        elif 'submit_transaction_form' in request.POST:
            transaction_form_submitted = TransactionForm(request.POST, user=request.user)
            if transaction_form_submitted.is_valid():
                transaction = transaction_form_submitted.save(commit=False)
                wallet = transaction_form_submitted.cleaned_data['wallet']
                transaction.wallet = wallet
                if transaction.type == 'Income':
                    wallet.balance += Decimal(transaction.amount)
                else:
                    wallet.balance -= Decimal(transaction.amount)
                total_balance = Decimal(sum(Decimal(w.balance) for w in Wallet.objects.filter(user=request.user)))
                if transaction.type == 'Income':
                    transaction.total_balance = total_balance + Decimal(transaction.amount)
                else:
                    transaction.total_balance = total_balance - Decimal(transaction.amount)
                transaction.save()
                wallet.save()
                return redirect('dashboard')
        
        transaction_id = request.POST.get('transaction_id')
        if transaction_id:
            transaction = get_object_or_404(Transaction, id=transaction_id)
            original_wallet = transaction.wallet
            original_type = transaction.type
            original_amount = Decimal(transaction.amount)
           
            if transaction.wallet.fat and transaction.wallet.fat.amount is not None:
                original_fat_amount = transaction.wallet.fat.amount
            else:
                original_fat_amount = Decimal(0.00)
            transaction_form_submitted = TransactionForm(request.POST, user=request.user, instance=transaction)

            if transaction_form_submitted.is_valid():
                if 'delete_transaction' in request.POST:
                    wallet = transaction.wallet
                    if transaction.type == 'Income':
                        wallet.balance -= Decimal(transaction.amount)

                    
                    elif transaction.type == 'Expense':
                        wallet.balance += Decimal(transaction.amount)

                    if transaction.type == 'Expense' and transaction.category == 'Balance Adjustment':
                        # print('code block works')
                        updated_fat_amount = transaction.amount
                        transaction.wallet.fat.amount = transaction.wallet.fat.amount - updated_fat_amount
                        transaction.wallet.fat.save()  
                        # if transaction.category == 'Balance Adjustment':
                        #     print(f'Current Fat: {wallet.fat.amount}')    
                    if transaction.type == 'Income' and transaction.category == 'Balance Adjustment':
                        updated_fat_amount = transaction.amount
                        transaction.wallet.fat.amount = transaction.wallet.fat.amount + updated_fat_amount
                        
                        transaction.wallet.fat.save()  
                        # print('code block works')

                    wallet.save()
                    transaction.delete()
                    messages.success(request, "Transaction deleted successfully!")
                    return redirect('dashboard')

                updated_transaction = transaction_form_submitted.save(commit=False)
                
                if original_wallet != updated_transaction.wallet:
                    if original_type == 'Income':
                        original_wallet.balance -= Decimal(original_amount)
                    elif original_type == 'Expense':
                        original_wallet.balance += Decimal(original_amount)
                    original_wallet.save()

                    new_wallet = updated_transaction.wallet
                    if updated_transaction.type == 'Income':
                        new_wallet.balance += Decimal(updated_transaction.amount)
                    elif updated_transaction.type == 'Expense':
                        new_wallet.balance -= Decimal(updated_transaction.amount)
                    new_wallet.save()
                else:
                    if original_type == 'Income':
                        original_wallet.balance -= Decimal(original_amount)
                    elif original_type == 'Expense':
                        original_wallet.balance += Decimal(original_amount)

                    if updated_transaction.type == 'Income':
                        original_wallet.balance += Decimal(updated_transaction.amount)
                    elif updated_transaction.type == 'Expense':
                        original_wallet.balance -= Decimal(updated_transaction.amount)

                    original_wallet.save()

                
                if updated_transaction.category == 'Balance Adjustment':
                    updated_fat_amount = updated_transaction.amount
                    

                    if updated_fat_amount > original_fat_amount:
                        fat_amount_difference = updated_fat_amount - original_fat_amount
                        updated_fat_amount = original_fat_amount + fat_amount_difference
                        updated_transaction.wallet.fat.amount = updated_fat_amount
                        updated_transaction.wallet.fat.save()
                    
                    elif updated_fat_amount < original_fat_amount:
                        fat_amount_difference = original_fat_amount - updated_fat_amount
                        updated_fat_amount = original_fat_amount - fat_amount_difference
                        updated_transaction.wallet.fat.amount = updated_fat_amount
                        updated_transaction.wallet.fat.save()

                
                total_balance = Decimal(sum(Decimal(w.balance) for w in Wallet.objects.filter(user=request.user)))
                updated_transaction.total_balance = total_balance
                updated_transaction.save()
                messages.success(request, "Transaction updated successfully!")
                return redirect('dashboard')
       
        wallet_id = request.POST.get('wallet_id')

        if wallet_id:
            wallet = get_object_or_404(Wallet, id=wallet_id, user=request.user)

            if 'delete_wallet' in request.POST:
                wallet.delete()
                messages.success(request, "Wallet deleted successfully!")
                return redirect('dashboard')

            wallet_form_submitted = WalletForm(request.POST, instance=wallet)
            
            initial_balance = Decimal(wallet.balance)
      
            if wallet_form_submitted.is_valid():
                updated_balance = Decimal(wallet_form_submitted.cleaned_data.get('balance'))
                fat_amount = Decimal(wallet.update_fat_balance(initial_balance))
               
               
                #expense transaction    
                if updated_balance < initial_balance: 
                   
                    previous_expense_sum = Decimal(Transaction.objects.filter(
                        wallet=wallet,
                        category='Balance Adjustment',
                        type='Expense'
                    ).aggregate(total_expenses=Sum('amount'))['total_expenses'] or Decimal('0.00'))
                   

                    previous_income_sum = Decimal(Transaction.objects.filter(
                        wallet=wallet,
                        type='Income',
                        category='Balance Adjustment',
                    ).aggregate(total_income=Sum('amount'))['total_income'] or Decimal('0.00'))
               
                    
                    adjusted_amount = Decimal(abs(fat_amount)) - Decimal(abs(previous_expense_sum))
                    adjusted_amount = Decimal(fat_amount) + Decimal(abs(previous_income_sum)) - Decimal(abs(previous_expense_sum))
                    adjusted_amount = Decimal(abs(adjusted_amount))
     
                    total_balance = Decimal(sum(Decimal(w.balance) for w in Wallet.objects.filter(user=request.user)))

                    Transaction.objects.create(
                            wallet=wallet,
                            type='Expense',
                            category='Balance Adjustment',
                            amount=adjusted_amount,
                            total_balance=total_balance - adjusted_amount,
                    )
                    messages.success(request, "Wallet updated with an expense record!")
                    
                #income transaction         
                elif updated_balance > initial_balance:
                   
                    previous_income_sum = Decimal(Transaction.objects.filter(
                        wallet=wallet,
                        type='Income',
                        category='Balance Adjustment',
                    ).aggregate(total_income=Sum('amount'))['total_income'] or Decimal('0.00'))
            

                    previous_expense_sum = Decimal(Transaction.objects.filter(
                        wallet=wallet,
                        category='Balance Adjustment',
                        type='Expense'
                    ).aggregate(total_expenses=Sum('amount'))['total_expenses'] or Decimal('0.00'))
                


                    adjusted_amount = Decimal(fat_amount) + Decimal(abs(previous_income_sum)) - Decimal(abs(previous_expense_sum))
                    adjusted_amount = Decimal(abs(adjusted_amount))
                    
                    if adjusted_amount > 0:
                        total_balance = Decimal(sum(Decimal(w.balance) for w in Wallet.objects.filter(user=request.user)))
                        Transaction.objects.create(
                            wallet=wallet,
                            type='Income',
                            category='Balance Adjustment',
                            amount=adjusted_amount,
                            total_balance=total_balance + adjusted_amount,
                        )
                        messages.success(request, "Wallet updated with an income record!")
                    else:
                        messages.info(request, "No additional income adjustment required.")
                                
                wallet.save()
                messages.success(request, "Wallet updated successfully!")
                return redirect('dashboard')                       
    
        transferform = WalletTransferForm(request.POST)
        transferform.fields['source_wallet'].queryset = Wallet.objects.filter(user=request.user)
        transferform.fields['destination_wallet'].queryset = Wallet.objects.filter(user=request.user)

        if transferform.is_valid():
            source_wallet = transferform.cleaned_data['source_wallet']
            destination_wallet = transferform.cleaned_data['destination_wallet']
            amount = transferform.cleaned_data['amount']

             # Deduct from source wallet
            source_wallet.balance -= Decimal(amount)
            source_wallet.save()

            # Add to destination wallet
            destination_wallet.balance += Decimal(amount)
            destination_wallet.save()


            # create a transaction
            total_balance = Decimal(sum(Decimal(w.balance) for w in Wallet.objects.filter(user=request.user)))
            # decrease
            Transaction.objects.create(
                    wallet=source_wallet,
                    type='Transfer',
                    category='Balance Adjustment Decrease',
                    amount=amount,
                    total_balance=total_balance,
            )

            Transaction.objects.create(
                    wallet=destination_wallet,
                    type='Transfer',
                    category='Balance Adjustment Increase',
                    amount=amount,
                    total_balance=total_balance,
            )


            messages.success(request, f"Transferred {amount} successfully from {source_wallet} to {destination_wallet}.")
            # return redirect('dashboard')  # Adjust to your desired redirect URL

        


    wallet_form = WalletForm()
    transaction_form = TransactionForm(user=request.user)
    is_dashboard = True
    wallets = Wallet.objects.filter(user=request.user)
    wallet_forms = {wallet.id: WalletForm(instance=wallet) for wallet in wallets}
    transactions = Transaction.objects.filter(wallet__user=request.user).order_by('-timestamp')
    for transaction in transactions:
        transaction.edit_form = TransactionForm(instance=transaction, user=request.user)
    
    total_fat = Decimal(Fat.objects.aggregate(total=Sum('amount'))['total'] or Decimal('0.00'))
    total_balance = Decimal(sum(Decimal(wallet.balance) for wallet in wallets))
    total_income = Decimal(Transaction.objects.filter(wallet__user=request.user, type='Income').aggregate(total=Sum('amount'))['total'] or Decimal('0.00'))
    total_expenses = Decimal(Transaction.objects.filter(wallet__user=request.user, type='Expense').aggregate(total=Sum('amount'))['total'] or Decimal('0.00'))
    net_balance = Decimal(total_income) - Decimal(total_expenses)
    
    # transfer form
    transferform = WalletTransferForm()
    transferform.fields['source_wallet'].queryset = Wallet.objects.filter(user=request.user)
    transferform.fields['destination_wallet'].queryset = Wallet.objects.filter(user=request.user)

    # filtering transactions
    filter_transactions_form = TransactionFilterForm(data=request.GET, user=request.user)
    if filter_transactions_form.is_valid():
        start_date = filter_transactions_form.cleaned_data.get('start_date')
        end_date = filter_transactions_form.cleaned_data.get('end_date')
        wallet = filter_transactions_form.cleaned_data.get('wallet')
        category = filter_transactions_form.cleaned_data.get('category')
        transaction_type = filter_transactions_form.cleaned_data.get('type')
        # Filter by transaction type
        if transaction_type:
            transactions = transactions.filter(type=transaction_type)


        # Filter by start date (ignore time)
        if start_date:
            start_datetime = timezone.make_aware(datetime.combine(start_date, datetime.min.time()))
            transactions = transactions.filter(timestamp__gte=start_datetime)

        # Filter by end date (set time to 23:59:59 if end date is provided)
        if end_date:
            # Combine the end_date with time 23:59:59 to include the full day
            end_date = timezone.make_aware(datetime.combine(end_date, datetime.max.time()))
            transactions = transactions.filter(timestamp__lte=end_date)

        # Filter by wallet
        if wallet:
            transactions = transactions.filter(wallet=wallet)

        # Filter by category
        if category:
            transactions = transactions.filter(category=category)

        if 'reset-btn' in request.GET:
            return redirect('dashboard')
    return render(request, 'dashboard/dashboard.html', {
        'wallets': wallets,
        'wallet_forms': wallet_forms,
        'transactions': transactions,
        'total_balance': total_balance,
        'wallet_form': wallet_form,
        'transaction_form': transaction_form,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_balance': net_balance,
        'total_fat': total_fat,
        'transferform':transferform,
        'filter_transactions_form':filter_transactions_form,
        'user': request.user,
        'is_dashboard':is_dashboard,
    })
