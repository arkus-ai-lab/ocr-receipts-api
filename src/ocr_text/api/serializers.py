from rest_framework import serializers
from core.models  import Receipt_eTransaction

class ProductSerializer(serializers.ModelSerializer):
    class Meta():
        model = Receipt_eTransaction
        fields = "__all__"