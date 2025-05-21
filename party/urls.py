from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    TokenRefreshView,
    UserViewSet,
    NewsCategoryViewSet,
    NewsViewSet,
    EventCategoryViewSet,
    EventViewSet,
    EventRegistrationViewSet,
    GalleryCategoryViewSet,
    GalleryViewSet,
    LeadershipPositionViewSet,
    NationalLeadershipViewSet,
    DonationViewSet,
    ProductCategoryViewSet,
    ProductViewSet,
    OrderViewSet,
    OrderItemViewSet,
    MembershipPlanViewSet,
    MembershipViewSet,
    CountyViewSet,
    ConstituencyViewSet,
    WardViewSet
)
from .views.newsletter import subscribe, verify_subscription, unsubscribe

router = DefaultRouter()

# Location URLs
router.register(r'counties', CountyViewSet, basename='county')
router.register(r'constituencies', ConstituencyViewSet, basename='constituency')
router.register(r'wards', WardViewSet, basename='ward')

# Other URLs
router.register(r'users', UserViewSet, basename='user')
router.register(r'news-categories', NewsCategoryViewSet)
router.register(r'news', NewsViewSet)
router.register(r'event-categories', EventCategoryViewSet)
router.register(r'events', EventViewSet)
router.register(r'event-registrations', EventRegistrationViewSet, basename='event-registration')
router.register(r'gallery-categories', GalleryCategoryViewSet)
router.register(r'gallery', GalleryViewSet)
router.register(r'leadership-positions', LeadershipPositionViewSet)
router.register(r'national-leadership', NationalLeadershipViewSet)
router.register(r'donations', DonationViewSet)
router.register(r'product-categories', ProductCategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'order-items', OrderItemViewSet)
router.register(r'membership-plans', MembershipPlanViewSet)
router.register(r'memberships', MembershipViewSet, basename='membership')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/newsletter/subscribe/', subscribe, name='newsletter_subscribe'),
    path('api/newsletter/verify/<str:token>/', verify_subscription, name='newsletter_verify'),
    path('api/newsletter/unsubscribe/', unsubscribe, name='newsletter_unsubscribe'),
] 