import logging

import requests
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from payapp.forms import SendMoneyForm, RequestMoneyForm
from payapp.models import Transaction, Request
from register.models import Account
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test

from decimal import Decimal
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import render

from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from .models import UserAccount, Transaction
from django.db import transaction as db_transaction
# from .utils import convert_currency
from decimal import Decimal

from .utils import fetch_currency_conversion


# Create your views here.
@login_required(login_url='/webapps2024/login')
def view_transactions(request):
    transaction_in = Transaction.objects.filter(Q(receiver=request.user))
    transaction_out = Transaction.objects.filter(Q(sender=request.user))

    return render(request, 'webapps2024/payapp/view_transactions.html',
                  {'transaction_in': transaction_in, 'transaction_out': transaction_out})


@csrf_protect
@transaction.atomic
@login_required(login_url='/webapps2024/login')
def view_requests(request):
    if request.method == 'POST':
        confirm = request.POST['confirm']
        status, request_in = confirm.split()

        req = Request.objects.get(id=request_in)

        if status == "accept":
            req.accepted = True

            sender = req.giver
            receiver = req.requester
            amount = req.amount

            t = Transaction(sender=sender, receiver=receiver, sent_amount=amount, received_amount=amount, sent_currency='GBP', received_currency='GBP')
            t.save()

            sender_account = Account.objects.get(user=sender)
            sender_account.amount -= amount
            sender_account.save()

            receiver_account = Account.objects.get(user=receiver)
            receiver_account.amount += amount
            receiver_account.save()

        req.pending = False
        req.save()

        return redirect('view_transactions')

    requests = Request.objects.filter(giver=request.user).filter(pending=True)
    return render(request, 'webapps2024/payapp/view_requests.html', {'requests': requests})


@staff_member_required
@login_required(login_url='/webapps2024/login')
def view_admin_transactions(request):
    transactions = Transaction.objects.all()

    return render(request, 'webapps2024/payapp/view_admin_transactions.html', {'transactions': transactions})


@staff_member_required
@login_required(login_url='/webapps2024/login')
def view_admin_requests(request):
    requests = Request.objects.all()

    return render(request, 'webapps2024/payapp/view_admin_requests.html', {'requests': requests})


@staff_member_required
@login_required(login_url='/webapps2024/login')
def view_admin_home(request):
    users = Account.objects.all().select_related('user')
    admins = User.objects.filter(is_superuser=True)

    return render(request, 'webapps2024/payapp/view_admin_home.html', {'users': users, 'admins': admins})


@login_required(login_url='/webapps2024/login')
@csrf_protect
@db_transaction.atomic
@login_required
def send_money(request):
    if request.method == 'POST':
        form = SendMoneyForm(request.POST)
        if form.is_valid():
            sender = request.user
            receiver = form.cleaned_data.get('receiver')
            sent_amount = Decimal(form.cleaned_data.get('amount'))

            if sender == receiver:
                messages.error(request, "Cannot send money to yourself.")
                return redirect("send_money")

            sender_account = get_object_or_404(Account, user=sender)
            receiver_account = get_object_or_404(Account, user=receiver)

            if sender_account.currency != receiver_account.currency:
                conversion_result = get_converted(sender_account.currency, receiver_account.currency, sent_amount)
                if conversion_result and 'converted_amount' in conversion_result:
                    received_amount = conversion_result['converted_amount']
                    received_currency = receiver_account.currency
                else:
                    error_message = conversion_result.get('error', 'Failed to convert currency.') if conversion_result else "Error accessing conversion service."
                    messages.error(request, error_message)
                    return redirect("send_money")
            else:
                received_amount = sent_amount
                received_currency = sender_account.currency

            if sent_amount > 0 and sender_account.amount >= sent_amount:
                sender_account.amount -= sent_amount
                receiver_account.amount += received_amount
                sender_account.save()
                receiver_account.save()

                Transaction.objects.create(
                    sender=sender,
                    receiver=receiver,
                    sent_amount=sent_amount,
                    received_amount=received_amount,
                    sent_currency=sender_account.currency,
                    received_currency=received_currency
                )

                messages.success(request, "Money sent successfully!")
                return redirect("home")
            else:
                messages.error(request, "Insufficient funds.")
                return redirect("send_money")
    else:
        form = SendMoneyForm()

    return render(request, 'webapps2024/payapp/send_money.html', {"form": form})

# THIS WORKS BUT DIPLCATE THE PAYMENT IN TRANSACTION"

# def send_money(request):
#     if request.method == 'POST':
#         form = SendMoneyForm(request.POST)
#         if form.is_valid():
#             sender = request.user
#             receiver = form.cleaned_data.get('receiver')
#             original_amount = Decimal(form.cleaned_data.get('amount'))
#
#             if sender == receiver:
#                 messages.error(request, "Cannot send money to yourself.")
#                 return redirect("send_money")
#
#             sender_account = get_object_or_404(Account, user=sender)
#             receiver_account = get_object_or_404(Account, user=receiver)
#
#             if sender_account.currency != receiver_account.currency:
#                 conversion_result = get_converted(sender_account.currency, receiver_account.currency, original_amount)
#                 if 'converted_amount' in conversion_result:
#                     converted_amount = conversion_result['converted_amount']
#                 else:
#                     messages.error(request, conversion_result.get('error', 'Failed to convert currency.'))
#                     return redirect("send_money")
#             else:
#                 converted_amount = original_amount
#
#             if original_amount > 0 and sender_account.amount >= original_amount:
#                 sender_account.amount -= original_amount
#                 receiver_account.amount += converted_amount
#                 sender_account.save()
#                 receiver_account.save()
#
#                 Transaction.objects.create(sender=sender, receiver=receiver, amount=original_amount, currency=sender_account.currency)
#                 Transaction.objects.create(sender=sender, receiver=receiver, amount=converted_amount, currency=receiver_account.currency)
#
#                 messages.success(request, "Money sent successfully!")
#                 return redirect("home")
#             else:
#                 messages.error(request, "Insufficient funds.")
#                 return redirect("send_money")
#     else:
#         form = SendMoneyForm()  # Initialize form for GET request
#
#     return render(request, 'webapps2024/payapp/send_money.html', {"form": form})

# @login_required(login_url='/webapps2024/login')
# @csrf_protect
# @db_transaction.atomic
# def send_money(request):
#     if request.method == 'POST':
#         form = SendMoneyForm(request.POST)
#         if form.is_valid():
#             sender = request.user
#             receiver = form.cleaned_data.get('receiver')
#             amount = Decimal(form.cleaned_data.get('amount'))
#
#             if sender == receiver:
#                 messages.error(request, "Cannot send money to yourself.")
#                 return redirect("send_money")
#
#             sender_account = get_object_or_404(Account, user=sender)
#             receiver_account = get_object_or_404(Account, user=receiver)
#
#             if sender_account.currency != receiver_account.currency:
#                 conversion_result = convert_currency(sender_account.currency, receiver_account.currency, amount)
#                 if 'converted_amount' in conversion_result:
#                     amount = conversion_result['converted_amount']
#                 else:
#                     messages.error(request, conversion_result.get('error', 'Failed to convert currency.'))
#                     return redirect("send_money")
#
#             if 0 < amount <= sender_account.amount:
#                 sender_account.amount -= amount
#                 receiver_account.amount += amount
#                 sender_account.save()
#                 receiver_account.save()
#
#                 Transaction.objects.create(sender=sender, receiver=receiver, amount=amount, currency=receiver_account.currency)
#                 messages.success(request, "Money sent successfully!")
#                 return redirect("home")
#             else:
#                 messages.error(request, "Insufficient funds.")
#                 return redirect("send_money")
#     else:
#         form = SendMoneyForm()
#
#     return render(request, 'webapps2024/payapp/send_money.html', {"form": form})

# @csrf_protect
# @transaction.atomic
# @login_required(login_url='/webapps2024/login')
# def send_money(request):
#     if request.method == 'POST':
#         form = SendMoneyForm(request.POST)
#         if form.is_valid():
#             sender = request.user
#             receiver = form.cleaned_data.get('receiver')
#             amount = form.cleaned_data.get('amount')
#
#             if sender == receiver:
#                 messages.error(request, "Cannot send to yourself")
#                 return redirect("send_money")
#
#             sender_account = Account.objects.get(user=sender)
#
#             if 0 < amount < 1000000 and sender_account.amount - amount > 0:
#                 # process_payment(request)
#                 t = Transaction(sender=sender, receiver=receiver, amount=amount)
#                 t.save()
#
#                 sender_account.amount -= amount
#                 sender_account.save()
#
#                 receiver_account = Account.objects.get(user=receiver)
#                 receiver_account.amount += amount
#                 receiver_account.save()
#
#                 return redirect("home")
#             else:
#                 messages.error(request, "Insufficient Funds")
#                 return redirect("send_money")
#     else:
#         form = SendMoneyForm()
#
#     return render(request, 'webapps2024/payapp/send_money.html', {"form": form})


@csrf_protect
@transaction.atomic
@login_required(login_url='/webapps2024/login')
def request_money(request):
    if request.method == 'POST':
        form = RequestMoneyForm(request.POST)
        if form.is_valid():
            requester = request.user
            giver = form.cleaned_data.get('giver')
            amount = Decimal(form.cleaned_data.get('amount'))

            if requester == giver:
                messages.error(request, "Cannot request money from yourself")
                return redirect("request_money")

            # Fetching the correct Account models
            requester_account = Account.objects.filter(user=requester).first()
            giver_account = Account.objects.filter(user=giver).first()

            if not requester_account or not giver_account:
                messages.error(request, "Account details missing for involved parties.")
                return redirect("request_money")

            if requester_account.currency != giver_account.currency:
                conversion_result = get_converted(requester_account.currency, giver_account.currency, amount)
                if conversion_result and 'converted_amount' in conversion_result:
                    amount = conversion_result['converted_amount']
                else:
                    error_message = conversion_result.get('error', 'Failed to convert currency.') if conversion_result else "Error accessing conversion service."
                    messages.error(request, error_message)
                    return redirect("request_money")

            if 0 < amount <= 1000000:
                Request.objects.create(requester=requester, giver=giver, amount=amount)
                messages.success(request, "Money request sent successfully.")
                return redirect("home")
            else:
                messages.error(request, "Invalid amount.")
                return redirect("request_money")
    else:
        form = RequestMoneyForm()

    return render(request, 'webapps2024/payapp/request_money.html', {"form": form})# def request_money(request):
#     if request.method == 'POST':
#         form = RequestMoneyForm(request.POST)
#         if form.is_valid():
#             requester = request.user
#             giver = form.cleaned_data.get('giver')
#             amount = form.cleaned_data.get('amount')
#
#             if requester == giver:
#                 messages.error(request, "Cannot request from yourself")
#                 return redirect("request_money")
#
#             if 0 < amount < 1000000:
#                 r = Request(requester=requester, giver=giver, amount=amount)
#                 r.save()
#             else:
#                 messages.error(request, "Insufficient Funds")
#                 return redirect("request_money")
#
#             return redirect("home")
#     else:
#         form = RequestMoneyForm()
#
#     return render(request, 'webapps2024/payapp/request_money.html', {"form": form})


# Helper function to check if user is superuser
def is_superuser(user):
    return user.is_authenticated and user.is_superuser


@login_required
@user_passes_test(is_superuser)
def register_admin(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = True  # or user.is_superuser = True depending on your needs
            user.save()
            return redirect('admin_dashboard')  # Redirect after POST
    else:
        form = UserCreationForm()
    return render(request, 'webapps2024/register/admin_registration.html', {'form': form})


def admin_dashboard(request):
    return None


logger = logging.getLogger(__name__)



def get_converted(currency1, currency2, amount):
    try:
        # Update the URL to include the '/api/' prefix
        response = requests.get(f"http://localhost:8000/api/conversion/{currency1}/{currency2}/{amount}/")
        if response.status_code == 200:
            data = response.json()
            if 'converted_amount' in data:
                return {'converted_amount': Decimal(data['converted_amount'])}
            else:
                return {'error': data.get('error', 'Unknown error')}
        else:
            return {'error': f'Error with status code: {response.status_code}'}
    except requests.exceptions.RequestException as e:
        return {'error': str(e)}


def convert_currency(currency1, currency2, amount):
    exchange_rates = {
        'USD': {'EUR': 0.92, 'GBP': 0.81},
        'EUR': {'USD': 1.09, 'GBP': 0.88},
        'GBP': {'USD': 1.24, 'EUR': 1.14},
    }
    try:
        rate = exchange_rates.get(currency1).get(currency2)
        if rate is None:
            return {'error': 'Unsupported currency pair'}

        converted_amount = Decimal(amount) * Decimal(rate)
        return {'converted_amount': converted_amount}
    except Exception as e:
        return {'error': str(e)}
# def convert_currency(request, currency1, currency2, amount_of_currency1):
#     exchange_rates = {
#         'USD': {'EUR': 0.92, 'GBP': 0.81},
#         'EUR': {'USD': 1.09, 'GBP': 0.88},
#         'GBP': {'USD': 1.24, 'EUR': 1.14},
#     }
#     try:
#         # Convert amount_of_currency1 to Decimal for accurate arithmetic operations
#         amount = Decimal(amount_of_currency1)
#
#         # Retrieve the exchange rate for the given currency pair
#         rate = exchange_rates.get(currency1, {}).get(currency2)
#
#         if rate is None:
#             # Log error if the currency pair is unsupported
#             logger.error(f"Unsupported currency pair: {currency1} to {currency2}")
#             return Response({'error': 'Unsupported currency provided'}, status=400)
#
#         # Calculate the converted amount using the retrieved rate
#         converted_amount = amount * Decimal(rate)
#
#         # Return the converted amount as a float
#         return Response({'converted_amount': float(converted_amount)})
#
#     except Exception as e:
#         # Log the exception and return an error response
#         logger.exception("Failed to convert currency due to an unexpected error")
#         return Response({'error': 'Invalid input or server error'}, status=500)


def show_conversion_form(request):
    return render(request, 'payapp/conversion_form.html')




from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.db import transaction as db_transaction
from decimal import Decimal
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from decimal import Decimal
from .models import UserAccount

# @api_view(['GET'])
def process_payment(request):
    print("IN processs")
    sender_id = request.user.id  # Assuming the sender is the logged-in user
    receiver_id = request.data.get('receiver_id')
    amount = Decimal(request.data.get('amount'))

    sender = get_object_or_404(UserAccount, id=sender_id)
    receiver = get_object_or_404(UserAccount, id=receiver_id)

    # Example comparison
    if sender.user_id != request.user.id:
        return HttpResponse("Sender ID does not match logged-in user", status=400)

    # Convert currency if necessary
    if sender.currency != receiver.currency:
        converted_data = convert_currency(request, sender.currency, receiver.currency)
        if 'converted_amount' in converted_data.data:
            amount = Decimal(converted_data.data['converted_amount'])
        else:
            return HttpResponse(converted_data.data['error'], status=400)

    # Process payment
    with db_transaction.atomic():
        if sender.balance >= amount:
            sender.balance -= amount
            receiver.balance += amount
            sender.save()
            receiver.save()
            return HttpResponse("Payment processed successfully")
        else:
            return HttpResponse("Insufficient funds", status=400)

# def process_payment(request):
#     sender_id = request.user.id  # Assuming the sender is the logged-in user
#     receiver_id = request.data.get('receiver_id')
#     amount = Decimal(request.data.get('amount'))
#
#     sender = get_object_or_404(UserAccount, id=sender_id)
#     receiver = get_object_or_404(UserAccount, id=receiver_id)
#
#     # Optionally, fetch register_account data to compare
#     sender_registered_account = get_object_or_404(RegisterAccount, user_id=sender_id)
#
#     # Example comparison
#     if sender_registered_account.user_id != sender.user_id:
#         return HttpResponse("Sender ID does not match registered account", status=400)
#
#     # Convert currency if necessary
#     if sender.currency != receiver.currency:
#         converted_data = convert_currency(request, sender.currency, receiver.currency)
#         if 'converted_amount' in converted_data.data:
#             amount = Decimal(converted_data.data['converted_amount'])
#         else:
#             return HttpResponse(converted_data.data['error'], status=400)
#
#     # Process payment
#     with db_transaction.atomic():
#         if sender.balance >= amount:
#             sender.balance -= amount
#             receiver.balance += amount
#             sender.save()
#             receiver.save()
#             return HttpResponse("Payment processed successfully")
#         else:
#             return HttpResponse("Insufficient funds", status=400)




# @api_view(['GET'])
# def process_payment(request):
#     # This assumes you're collecting 'sender_id', 'receiver_id', and 'amount' from a form submission
#     sender_id = request.POST.get('sender_id')
#     receiver_id = request.POST.get('receiver_id')
#     amount = Decimal(request.POST.get('amount'))
#
#     sender = get_object_or_404(UserAccount, id=sender_id)
#     receiver = get_object_or_404(UserAccount, id=receiver_id)
#
#     if sender.currency != receiver.currency:
#         amount = convert_currency(sender.currency, receiver.currency, amount)
#
#     with db_transaction.atomic():
#         if sender.balance >= amount:
#             sender.balance -= amount
#             receiver.balance += amount
#             Transaction.objects.create(sender=sender, receiver=receiver, amount=amount, currency=receiver.currency)
#             sender.save()
#             receiver.save()
#             return HttpResponse("Payment Successful")
#         else:
#             return HttpResponse("Insufficient funds")
#
#     return HttpResponse("Error processing the payment")


def fetch_currency_conversion(from_currency, to_currency, amount):
    url = f"http://localhost:8000/payapp/conversion/{from_currency}/{to_currency}/{amount}/"

    try:
        response = requests.get(url)
        response.raise_for_status()  # This will raise an exception for HTTP error responses
        # Assuming the API returns JSON with 'converted_amount' and possibly other data
        data = response.json()
        return data['converted_amount'], data.get('rate', None)
    except requests.RequestException as e:
        print(f"HTTP Request failed: {e}")
        return None, None


def convert_money_view(request):
    if request.method == 'POST':
        # Example: get these values from a form or URL parameters
        from_currency = request.POST.get('from_currency')
        to_currency = request.POST.get('to_currency')
        amount = Decimal(request.POST.get('amount'))

        converted_amount, rate = fetch_currency_conversion(from_currency, to_currency, amount)
        if converted_amount is not None:
            return render(request, 'conversion_result.html', {
                'original_amount': amount,
                'converted_amount': converted_amount,
                'from_currency': from_currency,
                'to_currency': to_currency,
                'rate': rate
            })
        else:
            # Handle error, maybe show a message to the user
            return render(request, 'conversion_result.html', {'error': 'Could not convert currency.'})

    return render(request, 'conversion_form.html')
