
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
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class CustomLoginView(LoginView):
    authentication_form = CustomLoginForm
    def get_success_url(self):
        # Redirect to the dashboard with the logged-in user's username
        return reverse('dashboard', kwargs={'user': self.request.user.username})




def homepage(request):
    context = {
        'LANGUAGES': settings.LANGUAGES,  # Pass LANGUAGES explicitly
    }
    return render(request, 'dashboard/homepage.html', context)


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
                return redirect(reverse('dashboard', kwargs={'user': request.user.username}))
        
            else:
                print("Form is invalid:", wallet_form_submitted.errors)
        elif 'submit_transaction_form' in request.POST:
            transaction_form_submitted = TransactionForm(request.POST, user=request.user)
            if transaction_form_submitted.is_valid():
                transaction = transaction_form_submitted.save(commit=False)
                wallet = transaction_form_submitted.cleaned_data['wallet']
                transaction.wallet = wallet
                if transaction.type == 'Income':
                    
                   
                    # Retrieve percentages from the form cleaned_data; default to None if not provided.
                    transaction.savings_percentage = transaction_form_submitted.cleaned_data.get("savings_percentage")
                    transaction.investment_percentage = transaction_form_submitted.cleaned_data.get("investment_percentage")
                    transaction.charity_percentage = transaction_form_submitted.cleaned_data.get("charity_percentage")
                    
                    # Also assign computed amounts (if you added these fields in your model)
                    transaction.savings_amount = transaction.amount * (transaction.savings_percentage or Decimal('0')) / Decimal('100')
                    transaction.investment_amount = transaction.amount * (transaction.investment_percentage or Decimal('0')) / Decimal('100')
                    transaction.charity_amount = transaction.amount * (transaction.charity_percentage or Decimal('0')) / Decimal('100')
            
                    
                    
                    
                    
                    try:
                        savings_wallet = Wallet.objects.get(user=request.user, name='Savings', is_predefined=True)
                        savings_wallet.balance +=  transaction.savings_amount
                        savings_wallet.save()
                    except Wallet.DoesNotExist:
                        # Optionally, handle the missing wallet (e.g., log an error)
                        pass

                    # Update the Investment Wallet.
                    try:
                        investment_wallet = Wallet.objects.get(user=request.user, name='Investment', is_predefined=True)
                        investment_wallet.balance += transaction.investment_amount
                        investment_wallet.save()
                    except Wallet.DoesNotExist:
                        pass

                    # Update the Charity Wallet.
                    try:
                        charity_wallet = Wallet.objects.get(user=request.user, name='Charity', is_predefined=True)
                        charity_wallet.balance +=  transaction.charity_amount
                        charity_wallet.save()
                    except Wallet.DoesNotExist:
                        pass

                    cleared_balance = transaction.amount - (transaction.savings_amount + transaction.investment_amount + transaction.charity_amount)
                    wallet.balance += Decimal(cleared_balance)
                    total_balance = Decimal(sum(Decimal(w.balance) for w in Wallet.objects.filter(user=request.user)))
                    transaction.total_balance = total_balance + Decimal(cleared_balance)
                    
                else:
                    wallet.balance -= Decimal(transaction.amount)
                
                if transaction.type == 'Income':
                    pass
                   
                else:
                    
                    total_balance = Decimal(sum(Decimal(w.balance) for w in Wallet.objects.filter(user=request.user)))
                    transaction.total_balance = total_balance - Decimal(transaction.amount)
                transaction.save()
                wallet.save()
                return redirect(reverse('dashboard', kwargs={'user': request.user.username}))
            else:
                transaction_form = TransactionForm(user=request.user)

        elif 'delete_balance_adjustment' in request.POST:
            transaction_id = request.POST.get('transaction_id')
            transaction = get_object_or_404(Transaction, id=transaction_id)
            # print(f"POST request received for transaction ID: {transaction_id}")
        
            wallet = transaction.wallet
            if transaction.type == 'Income': 
                wallet.balance -= Decimal(transaction.amount)


            
            elif transaction.type == 'Expense':
                wallet.balance += Decimal(transaction.amount)
                print("Form is valid:")

            if transaction.type == 'Expense' and transaction.category == 'Balance Adjustment':
                # print('code block works')
                updated_fat_amount = transaction.amount
                transaction.wallet.fat.amount = transaction.wallet.fat.amount + updated_fat_amount
                transaction.wallet.fat.save()  
                
            if transaction.type == 'Income' and transaction.category == 'Balance Adjustment':
                updated_fat_amount = transaction.amount
                transaction.wallet.fat.amount = transaction.wallet.fat.amount - updated_fat_amount
                
                transaction.wallet.fat.save()  
                # print('code block works')

            
            wallet.save()
            transaction.delete()
            messages.success(request, "Transaction deleted successfully!")
            return redirect(reverse('dashboard', kwargs={'user': request.user.username}))


        # edit or delete transaction form
        transaction_id = request.POST.get('transaction_id')
        if transaction_id:
            transaction = get_object_or_404(Transaction, id=transaction_id)
            original_wallet = transaction.wallet
            original_type = transaction.type
            original_amount = Decimal(transaction.amount)
            transaction_form_submitted = TransactionForm(request.POST, user=request.user, instance=transaction)

            if transaction_form_submitted.is_valid():
              
                if 'delete_transaction' in request.POST:
                    print("Delete transaction condition triggered")
                    # print("POST data:", request.POST)
                    wallet = transaction.wallet
                    if transaction.type == 'Income':

                        cleared_balance = transaction.amount - (transaction.savings_amount+transaction.investment_amount+transaction.charity_amount)

                        wallet.balance -= Decimal(cleared_balance)


                        try:
                            savings_wallet = Wallet.objects.get(user=request.user, name='Savings', is_predefined=True)
                            savings_wallet.balance -=  transaction.savings_amount
                            savings_wallet.save()
                        except Wallet.DoesNotExist:
                            # Optionally, handle the missing wallet (e.g., log an error)
                            pass

                        # Update the Investment Wallet.
                        try:
                            investment_wallet = Wallet.objects.get(user=request.user, name='Investment', is_predefined=True)
                            investment_wallet.balance -= transaction.investment_amount
                            investment_wallet.save()
                        except Wallet.DoesNotExist:
                            pass

                        # Update the Charity Wallet.
                        try:
                            charity_wallet = Wallet.objects.get(user=request.user, name='Charity', is_predefined=True)
                            charity_wallet.balance -=  transaction.charity_amount
                            charity_wallet.save()
                        except Wallet.DoesNotExist:
                            pass
                    
                    elif transaction.type == 'Expense':
                        
                        wallet.balance += Decimal(transaction.amount)
                        
                    wallet.save()
                    transaction.delete()
                    messages.success(request, "Transaction deleted successfully!")
                    return redirect(reverse('dashboard', kwargs={'user': request.user.username}))

                updated_transaction = transaction_form_submitted.save(commit=False)
                
                # cleared_balance = updated_transaction.amount - (updated_transaction.savings_amount+updated_transaction.investment_amount+updated_transaction.charity_amount)                 
                if original_wallet != updated_transaction.wallet:
                    if original_type == 'Income':     
                        cleared_balance = updated_transaction.amount - (updated_transaction.savings_amount+updated_transaction.investment_amount+updated_transaction.charity_amount)                 
                        original_wallet.balance -= Decimal(cleared_balance)
                    elif original_type == 'Expense':
                        # REVERSE PREDEFINED WALLETS AMOUNTS
                        try:
                            savings_wallet = Wallet.objects.get(user=request.user, name='Savings', is_predefined=True)
                            savings_wallet.balance -=  updated_transaction.savings_amount
                            savings_wallet.save()
                            updated_transaction.savings_amount = Decimal(0.00)
                            
                        except Wallet.DoesNotExist:
                            # Optionally, handle the missing wallet (e.g., log an error)
                            pass

                        # Update the Investment Wallet.
                        try:
                            investment_wallet = Wallet.objects.get(user=request.user, name='Investment', is_predefined=True)
                            investment_wallet.balance -= updated_transaction.investment_amount
                            investment_wallet.save()
                            updated_transaction.investment_amount = Decimal(0.00)
                        except Wallet.DoesNotExist:
                            pass

                        # Update the Charity Wallet.
                        try:
                            charity_wallet = Wallet.objects.get(user=request.user, name='Charity', is_predefined=True)
                            charity_wallet.balance -=  updated_transaction.charity_amount
                            charity_wallet.save()
                            updated_transaction.charity_amount = Decimal(0.00)
                        except Wallet.DoesNotExist:
                            pass



                        original_wallet.balance += Decimal(original_amount)
                    original_wallet.save()

                    new_wallet = updated_transaction.wallet
                    if updated_transaction.type == 'Income':
                        if updated_transaction.savings_amount == 0 and updated_transaction.investment_amount == 0 and updated_transaction.charity_amount == 0:
                             # Also assign computed amounts (if you added these fields in your model)
                            updated_transaction.savings_amount = transaction.amount * (transaction.savings_percentage or Decimal('0')) / Decimal('100')
                            updated_transaction.investment_amount = transaction.amount * (transaction.investment_percentage or Decimal('0')) / Decimal('100')
                            updated_transaction.charity_amount = transaction.amount * (transaction.charity_percentage or Decimal('0')) / Decimal('100')
                    
                            try:
                                savings_wallet = Wallet.objects.get(user=request.user, name='Savings', is_predefined=True)
                                savings_wallet.balance +=  updated_transaction.savings_amount
                                savings_wallet.save()
                            except Wallet.DoesNotExist:
                                # Optionally, handle the missing wallet (e.g., log an error)
                                pass

                            # Update the Investment Wallet.
                            try:
                                investment_wallet = Wallet.objects.get(user=request.user, name='Investment', is_predefined=True)
                                investment_wallet.balance += updated_transaction.investment_amount
                                investment_wallet.save()
                            except Wallet.DoesNotExist:
                                pass

                            # Update the Charity Wallet.
                            try:
                                charity_wallet = Wallet.objects.get(user=request.user, name='Charity', is_predefined=True)
                                charity_wallet.balance +=  updated_transaction.charity_amount
                                charity_wallet.save()
                            except Wallet.DoesNotExist:
                                pass
                        cleared_balance = updated_transaction.amount - (updated_transaction.savings_amount+updated_transaction.investment_amount+updated_transaction.charity_amount)                 
                        new_wallet.balance += Decimal(cleared_balance)
                    elif updated_transaction.type == 'Expense':
                        # REVERSE PREDEFINED WALLETS AMOUNTS
                        try:
                            savings_wallet = Wallet.objects.get(user=request.user, name='Savings', is_predefined=True)
                            savings_wallet.balance -=  updated_transaction.savings_amount
                            savings_wallet.save()
                            updated_transaction.savings_amount = Decimal(0.00)
                        except Wallet.DoesNotExist:
                            # Optionally, handle the missing wallet (e.g., log an error)
                            pass

                        # Update the Investment Wallet.
                        try:
                            investment_wallet = Wallet.objects.get(user=request.user, name='Investment', is_predefined=True)
                            investment_wallet.balance -= updated_transaction.investment_amount
                            investment_wallet.save()
                            updated_transaction.investment_amount = Decimal(0.00)
                        except Wallet.DoesNotExist:
                            pass

                        # Update the Charity Wallet.
                        try:
                            charity_wallet = Wallet.objects.get(user=request.user, name='Charity', is_predefined=True)
                            charity_wallet.balance -=  updated_transaction.charity_amount
                            charity_wallet.save()
                            updated_transaction.charity_amount = Decimal(0.00)
                        except Wallet.DoesNotExist:
                            pass


                        new_wallet.balance -= Decimal(updated_transaction.amount)
                    new_wallet.save()
                else: 
                    # Retrieve the predefined wallets (they must exist)
                    try:
                        savings_wallet = Wallet.objects.get(user=request.user, name='Savings', is_predefined=True)
                    except Wallet.DoesNotExist:
                        savings_wallet = None

                    try:
                        investment_wallet = Wallet.objects.get(user=request.user, name='Investment', is_predefined=True)
                    except Wallet.DoesNotExist:
                        investment_wallet = None

                    try:
                        charity_wallet = Wallet.objects.get(user=request.user, name='Charity', is_predefined=True)
                    except Wallet.DoesNotExist:
                        charity_wallet = None

                    
                     # CASE 1: Changing from Expense to Income
                    if original_type == 'Expense' and updated_transaction.type == 'Income':
                        # 1. Revert the full expense effect by adding back the old transaction amount to the original wallet.
                        original_wallet.balance += transaction.amount
                        original_wallet.save()
                        # 2. (Now, the original wallet is “restored” as if the transaction were never an expense.)
                        # 3. Calculate new allocations based on the updated amount and percentages.
                        updated_amount = updated_transaction.amount
                        new_savings = updated_amount * (updated_transaction.savings_percentage or Decimal('0')) / Decimal('100')
                        new_investment = updated_amount * (updated_transaction.investment_percentage or Decimal('0')) / Decimal('100')
                        new_charity = updated_amount * (updated_transaction.charity_percentage or Decimal('0')) / Decimal('100')
                        total_allocated = new_savings + new_investment + new_charity

                        # 4. Deduct the new allocations from the original wallet.
                        original_wallet.balance += updated_amount - total_allocated 
                        original_wallet.save()

                        # 5. Update the predefined wallets by adding the new allocated amounts.
                        if savings_wallet:
                            savings_wallet.balance += new_savings
                            savings_wallet.save()
                        if investment_wallet:
                            investment_wallet.balance += new_investment
                            investment_wallet.save()
                        if charity_wallet:
                            charity_wallet.balance += new_charity
                            charity_wallet.save()

                        #  6. Update the allocation fields on the transaction.
                        updated_transaction.savings_amount = new_savings
                        updated_transaction.investment_amount = new_investment
                        updated_transaction.charity_amount = new_charity
                       
                            
                        # total_allocated = updated_transaction.savings_amount + updated_transaction.investment_amount + updated_transaction.charity_amount
                        
                        # original_wallet.balance = updated_amount - total_allocated 
                          
                   # CASE 2: Updating an Income Transaction (Income → Income)
                    elif original_type == 'Income' and updated_transaction.type == 'Income':
                        # 1. Reverse the previous allocations by subtracting the old allocated amounts from the predefined wallets.
                        updated_amount = updated_transaction.amount    
                        if savings_wallet:
                            savings_wallet.balance -= transaction.savings_amount or Decimal('0')
                            savings_wallet.save()
                        if investment_wallet:
                            investment_wallet.balance -= transaction.investment_amount or Decimal('0')
                            investment_wallet.save()
                        if charity_wallet:
                            charity_wallet.balance -= transaction.charity_amount or Decimal('0')
                            charity_wallet.save()

                        # 2. Calculate new allocated amounts.
                        new_savings = updated_amount * (updated_transaction.savings_percentage or Decimal('0')) / Decimal('100')
                        new_investment = updated_amount * (updated_transaction.investment_percentage or Decimal('0')) / Decimal('100')
                        new_charity = updated_amount * (updated_transaction.charity_percentage or Decimal('0')) / Decimal('100')
                        total_allocated = new_savings + new_investment + new_charity

                        # 3. Update the original wallet so that its balance becomes the updated amount minus the new allocations.
                        original_wallet.balance += updated_amount - total_allocated
                        original_wallet.save()

                        # 4. Add the new allocated amounts to the predefined wallets.
                        if savings_wallet:
                            savings_wallet.balance += new_savings
                            savings_wallet.save()
                        if investment_wallet:
                            investment_wallet.balance += new_investment
                            investment_wallet.save()
                        if charity_wallet:
                            charity_wallet.balance += new_charity
                            charity_wallet.save()

                        # 5. Update the transaction's allocation fields.
                        updated_transaction.savings_amount = new_savings
                        updated_transaction.investment_amount = new_investment
                        updated_transaction.charity_amount = new_charity

                                    

                    elif updated_transaction.type == 'Expense':
                          # Step 1: Reverse the previous allocation
                        try:
                            savings_wallet = Wallet.objects.get(user=request.user, name='Savings', is_predefined=True)
                            savings_wallet.balance -= transaction.savings_amount  # Remove previous allocation
                            savings_wallet.save()
                        except Wallet.DoesNotExist:
                            pass  

                        try:
                            investment_wallet = Wallet.objects.get(user=request.user, name='Investment', is_predefined=True)
                            investment_wallet.balance -= transaction.investment_amount  # Remove previous allocation
                            investment_wallet.save()
                        except Wallet.DoesNotExist:
                            pass  

                        try:
                            charity_wallet = Wallet.objects.get(user=request.user, name='Charity', is_predefined=True)
                            charity_wallet.balance -= transaction.charity_amount  # Remove previous allocation
                            charity_wallet.save()
                        except Wallet.DoesNotExist:
                            pass  

                        updated_amount = updated_transaction.amount
                        # Instead of deducting the full updated_amount, we only deduct what was actually used
                        amount_to_deduct = updated_amount - (updated_transaction.savings_amount + updated_transaction.investment_amount + updated_transaction.charity_amount)
                        # total_allocated = updated_transaction.savings_amount + updated_transaction.investment_amount + updated_transaction.charity_amount
                        
                        original_wallet.balance -= Decimal(updated_amount + amount_to_deduct)

                        # 4. Reset all allocation fields for the expense.
                        updated_transaction.savings_percentage = Decimal('0')
                        updated_transaction.investment_percentage = Decimal('0')
                        updated_transaction.charity_percentage = Decimal('0')
                        updated_transaction.savings_amount = Decimal('0')
                        updated_transaction.investment_amount = Decimal('0')
                        updated_transaction.charity_amount = Decimal('0')

                    original_wallet.save()
               
                total_balance = Decimal(sum(Decimal(w.balance) for w in Wallet.objects.filter(user=request.user)))
                updated_transaction.total_balance = total_balance
                updated_transaction.save()
                messages.success(request, "Transaction updated successfully!")
                return redirect(reverse('dashboard', kwargs={'user': request.user.username}))
        
            
        wallet_id = request.POST.get('wallet_id')

        if wallet_id:
            wallet = get_object_or_404(Wallet, id=wallet_id, user=request.user)

            if 'delete_wallet' in request.POST:
                wallet.delete()
                messages.success(request, "Wallet deleted successfully!")
                return redirect(reverse('dashboard', kwargs={'user': request.user.username}))

            wallet_form_submitted = WalletForm(request.POST, instance=wallet)
            
            initial_balance = Decimal(wallet.balance)
      
            if wallet_form_submitted.is_valid():
                updated_balance = Decimal(wallet_form_submitted.cleaned_data.get('balance'))
                fat_amount = Decimal(wallet.update_fat_balance(initial_balance))
               
               
                #expense transaction    
                if updated_balance < initial_balance: 
                   
                    previous_expense_sum = Decimal(Transaction.objects.filter(
                        wallet=wallet,
                        category=_('Balance Adjustment'),
                        type='Expense'
                    ).aggregate(total_expenses=Sum('amount'))['total_expenses'] or Decimal('0.00'))
                   

                    previous_income_sum = Decimal(Transaction.objects.filter(
                        wallet=wallet,
                        type='Income',
                        category='Balance Adjustment',
                    ).aggregate(total_income=Sum('amount'))['total_income'] or Decimal('0.00'))
               
                    
                    adjusted_amount = Decimal(abs(fat_amount)) - Decimal(abs(previous_expense_sum))
                    adjusted_amount = Decimal(fat_amount) - Decimal(abs(previous_income_sum)) + Decimal(abs(previous_expense_sum))
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
                


                    adjusted_amount = Decimal(fat_amount) - Decimal(abs(previous_income_sum)) + Decimal(abs(previous_expense_sum))
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
                return redirect(reverse('dashboard', kwargs={'user': request.user.username}))                     
    
        # transfer form
        transferform = WalletTransferForm(request.POST, user=request.user)
       

        if transferform.is_valid():
            source_wallet = transferform.cleaned_data['source_wallet']
            destination_wallet = transferform.cleaned_data['destination_wallet']
            amount = transferform.cleaned_data['amount']
            use_fat_amount = transferform.cleaned_data.get('use_fat_amount')
            fat_wallet = transferform.cleaned_data.get('fat_wallet')
             # Deduct from source wallet
            source_wallet.balance -= Decimal(amount)
            source_wallet.save()

            # Add to destination wallet
            destination_wallet.balance += Decimal(amount)
            destination_wallet.save()


            # handle fat decreasing
            if use_fat_amount and fat_wallet:
                fat_wallet.fat.amount += amount
                fat_wallet.fat.save()


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
            return redirect(reverse('dashboard', kwargs={'user': request.user.username}))
        
    wallet_form = WalletForm()
    transaction_form = TransactionForm(user=request.user)
    is_dashboard = True
    wallets = Wallet.objects.filter(user=request.user)
    wallet_forms = {wallet.id: WalletForm(instance=wallet) for wallet in wallets}
    transactions = Transaction.objects.filter(wallet__user=request.user).order_by('-timestamp')
    for transaction in transactions:
        transaction.edit_form = TransactionForm(instance=transaction, user=request.user)
    
    total_fat = Decimal(Fat.objects.filter(wallet__user=request.user).aggregate(total=Sum('amount'))['total'] or Decimal('0.00'))
    total_balance = Decimal(sum(Decimal(wallet.balance) for wallet in wallets))
    total_income = Decimal(Transaction.objects.filter(wallet__user=request.user, type='Income').aggregate(total=Sum('amount'))['total'] or Decimal('0.00'))
    total_expenses = Decimal(Transaction.objects.filter(wallet__user=request.user, type='Expense').aggregate(total=Sum('amount'))['total'] or Decimal('0.00'))
    net_balance = Decimal(total_income) - Decimal(total_expenses)
    
    # transfer form
    transferform = WalletTransferForm(user=request.user)
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

        # Calculate totals for the filtered transactions
        total_income = transactions.filter(type='Income').aggregate(total=Sum('amount'))['total'] or 0
        total_expenses = transactions.filter(type='Expense').aggregate(total=Sum('amount'))['total'] or 0
        net_balance = total_income - total_expenses

        for transaction in transactions:
            transaction.edit_form = TransactionForm(instance=transaction, user=request.user)

        if 'reset-btn' in request.GET:
            return redirect(reverse('dashboard', kwargs={'user': request.user.username}))
        # Pass the totals to the template
        context = {
            
            'transactions': transactions,
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_balance': net_balance,
            'is_dashboard':True,
            'wallets': wallets,
            'wallet_forms': wallet_forms,
           
            'wallet_form': wallet_form,
            'total_balance': total_balance,
            'total_fat': total_fat,
            'transferform':transferform,
            'filter_transactions_form':filter_transactions_form,
            'user': request.user,
            'transaction_form': transaction_form,
        }
        return render(request, 'dashboard/dashboard.html', context)

  
    return render(request, 'dashboard/dashboard.html',  {
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
