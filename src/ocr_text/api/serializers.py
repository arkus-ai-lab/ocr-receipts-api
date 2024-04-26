from rest_framework import serializers
from core.models import Receipt

class Receipt(serializers.ModelSerializer):
    class Meta():
        model = Receipt
        fields = "__all__"