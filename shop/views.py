from rest_framework import viewsets
from .models import PickupLocation
from .serializers import PickupLocationSerializer

class PickupLocationViewSet(viewsets.ModelViewSet):
    queryset = PickupLocation.objects.filter(is_active=True)
    serializer_class = PickupLocationSerializer 