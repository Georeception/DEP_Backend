from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PickupLocationViewSet

router = DefaultRouter()
router.register(r'pickup-locations', PickupLocationViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 