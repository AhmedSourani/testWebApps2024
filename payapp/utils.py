# payapp/utils.py

EXCHANGE_RATES = {
    'GBP': {'USD': 1.25, 'EUR': 1.10},
    'USD': {'GBP': 0.80, 'EUR': 0.88},
    'EUR': {'GBP': 0.91, 'USD': 1.14},
}

def convert_currency(from_currency, to_currency, amount):
    rate = EXCHANGE_RATES.get(from_currency, {}).get(to_currency)
    if rate is None:
        raise ValueError("Currency conversion rate not available.")
    return amount * rate


def fetch_currency_conversion():
    return None