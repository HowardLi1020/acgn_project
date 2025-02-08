from rest_framework import serializers
from cart.models import PaymentTransactions

class PaymentTransactionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransactions
        fileds = [
            'payment_id', 'payment_method', 'payment_status', 'payment_date', 'payment_amount', 'transaction_id'
        ]