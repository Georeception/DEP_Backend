"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from party.views.views import (
    RegisterView, LoginView, LogoutView, UserDetailView,
    NewsViewSet, NewsCategoryViewSet, NewsDetailView,
    EventViewSet, EventCategoryViewSet, EventRegistrationViewSet,
    GalleryViewSet, GalleryCategoryViewSet,
    NationalLeadershipViewSet, LeadershipPositionViewSet,
    DonationViewSet, ProductViewSet, ProductCategoryViewSet,
    OrderViewSet, OrderItemViewSet, MembershipPlanViewSet,
    MembershipViewSet, UserViewSet, CountyViewSet,
    ConstituencyViewSet, WardViewSet
)
from party.views.newsletter import subscribe, verify_subscription, unsubscribe

router = DefaultRouter()
router.register(r'news', NewsViewSet)
router.register(r'news-categories', NewsCategoryViewSet)
router.register(r'events', EventViewSet)
router.register(r'event-categories', EventCategoryViewSet)
router.register(r'event-registrations', EventRegistrationViewSet, basename='event-registration')
router.register(r'gallery', GalleryViewSet)
router.register(r'gallery-categories', GalleryCategoryViewSet)
router.register(r'leadership', NationalLeadershipViewSet)
router.register(r'leadership-positions', LeadershipPositionViewSet)
router.register(r'donations', DonationViewSet)
router.register(r'products', ProductViewSet)
router.register(r'product-categories', ProductCategoryViewSet)
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'order-items', OrderItemViewSet)
router.register(r'membership-plans', MembershipPlanViewSet)
router.register(r'memberships', MembershipViewSet, basename='membership')
router.register(r'users', UserViewSet)
router.register(r'counties', CountyViewSet)
router.register(r'constituencies', ConstituencyViewSet, basename='constituency')
router.register(r'wards', WardViewSet, basename='ward')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/register/', RegisterView.as_view(), name='auth-register'),
    path('api/auth/login/', LoginView.as_view(), name='auth-login'),
    path('api/auth/logout/', LogoutView.as_view(), name='auth-logout'),
    path('api/auth/user/', UserDetailView.as_view(), name='auth-user-detail'),
    path('api/newsletter/subscribe/', subscribe, name='newsletter-subscribe'),
    path('api/newsletter/verify/<str:token>/', verify_subscription, name='newsletter-verify'),
    path('api/newsletter/unsubscribe/', unsubscribe, name='newsletter-unsubscribe'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
