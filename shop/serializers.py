from rest_framework import serializers
from .models import PickupLocation

class PickupLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PickupLocation
        fields = ['id', 'name', 'address', 'city', 'state', 'zip_code', 'phone', 'email', 'is_active'] 