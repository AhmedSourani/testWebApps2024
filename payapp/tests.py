from django.test import TestCase

# Create your tests here.


from django.test import TestCase, Client
from django.urls import reverse

class CurrencyConversionTest(TestCase):
    def test_conversion(self):
        client = Client()
        response = client.get(reverse('convert_currency', args=('USD', 'EUR', '100')))
        self.assertEqual(response.status_code, 200)
        self.assertIn('converted_amount', response.json())

        # Test unsupported currency
        response = client.get(reverse('convert_currency', args=('USD', 'XXX', '100')))
        self.assertEqual(response.status_code, 404)

