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


# Create your views here.
@login_required(login_url='/webapps2024/login')
def view_transactions(request):
    transaction_in = Transaction.objects.filter(Q(receiver=request.user))
    transaction_out = Transaction.objects.filter(Q(sender=request.user))

    return render(request, 'webapps2024/payapp/view_transactions.html', {'transaction_in': transaction_in, 'transaction_out': transaction_out})


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

            t = Transaction(sender=sender, receiver=receiver, amount=amount)
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


@csrf_protect
@transaction.atomic
@login_required(login_url='/webapps2024/login')
def send_money(request):
    if request.method == 'POST':
        form = SendMoneyForm(request.POST)
        if form.is_valid():
            sender = request.user
            receiver = form.cleaned_data.get('receiver')
            amount = form.cleaned_data.get('amount')

            if sender == receiver:
                messages.error(request, "Cannot send to yourself")
                return redirect("send_money")

            sender_account = Account.objects.get(user=sender)

            if 0 < amount < 1000000 and sender_account.amount - amount > 0:
                t = Transaction(sender=sender, receiver=receiver, amount=amount)
                t.save()

                sender_account.amount -= amount
                sender_account.save()

                receiver_account = Account.objects.get(user=receiver)
                receiver_account.amount += amount
                receiver_account.save()

                return redirect("home")
            else:
                messages.error(request, "Insufficient Funds")
                return redirect("send_money")
    else:
        form = SendMoneyForm()

    return render(request, 'webapps2024/payapp/send_money.html', {"form":form})


@csrf_protect
@transaction.atomic
@login_required(login_url='/webapps2024/login')
def request_money(request):
    if request.method == 'POST':
        form = RequestMoneyForm(request.POST)
        if form.is_valid():
            requester = request.user
            giver = form.cleaned_data.get('giver')
            amount = form.cleaned_data.get('amount')

            if requester == giver:
                messages.error(request, "Cannot request from yourself")
                return redirect("request_money")

            if 0 < amount < 1000000:
                r = Request(requester=requester, giver=giver, amount=amount)
                r.save()
            else:
                messages.error(request, "Insufficient Funds")
                return redirect("request_money")

            return redirect("home")
    else:
        form = RequestMoneyForm()

    return render(request, 'webapps2024/payapp/request_money.html', {"form":form})
