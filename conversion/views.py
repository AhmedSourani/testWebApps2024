# conversion/views.py

from django.http import JsonResponse
from decimal import Decimal


# def convert_currency(request, currency1, currency2, amount_of_currency1):
#     exchange_rates = {
#         'USD': {'EUR': 0.92, 'GBP': 0.81},
#         'EUR': {'USD': 1.09, 'GBP': 0.88},
#         'GBP': {'USD': 1.24, 'EUR': 1.14},
#     }
#
#     try:
#         amount = Decimal(amount_of_currency1)
#         rate = exchange_rates.get(currency1, {}).get(currency2)
#
#         if rate is None:
#             return JsonResponse({'error': 'Unsupported currency pair'}, status=404)
#
#         converted_amount = amount * Decimal(rate)
#         return JsonResponse({'converted_amount': float(converted_amount), 'rate': rate})
#
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=400)
def convert_currency(request, currency1, currency2, amount_of_currency1):
    print(f"Currency1: {currency1}, Currency2: {currency2}, Amount: {amount_of_currency1}")
    exchange_rates = {
        'USD': {'EUR': 0.92, 'GBP': 0.81},
        'EUR': {'USD': 1.09, 'GBP': 0.88},
        'GBP': {'USD': 1.24, 'EUR': 1.14},
    }

    try:
        amount = Decimal(amount_of_currency1)
        rate = exchange_rates.get(currency1, {}).get(currency2)
        print(f"Rate found: {rate}")

        if rate is None:
            return JsonResponse({'error': 'Unsupported currency pair'}, status=404)

        converted_amount = amount * Decimal(rate)
        return JsonResponse({'converted_amount': float(converted_amount), 'rate': rate})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
