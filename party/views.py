from rest_framework import viewsets
from .models import PickupLocation
from .serializers import PickupLocationSerializer

class PickupLocationViewSet(viewsets.ModelViewSet):
    queryset = PickupLocation.objects.all()
    serializer_class = PickupLocationSerializer 