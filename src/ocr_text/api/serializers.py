from rest_framework import serializers
from core.models  import Receipt_eTransaction
from core.models import Receipt

class ProductSerializer(serializers.ModelSerializer):
    class Meta():
        model = Receipt_eTransaction
        fields = "__all__"

class Receipt(serializers.ModelSerializer):
    class Meta():
        model = Receipt
        fields = "__all__"