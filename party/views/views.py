import json
import logging
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from django.conf import settings
from django.db import IntegrityError, transaction
from django.shortcuts import render
from rest_framework import generics, status, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth import get_user_model, authenticate
from django.utils import timezone
from ..models import (
    User, News, NewsCategory, Event, EventCategory, EventRegistration, Gallery, GalleryCategory,
    NationalLeadership, LeadershipPosition, Donation, Product, ProductCategory, Order, OrderItem,
    MembershipPlan, Membership
)
from ..serializers import (
    UserRegistrationSerializer, UserSerializer,
    NewsSerializer, NewsCategorySerializer,
    EventSerializer, EventCategorySerializer, EventRegistrationSerializer,
    GallerySerializer, GalleryCategorySerializer, NationalLeadershipSerializer,
    LeadershipPositionSerializer, DonationSerializer, ProductSerializer,
    ProductCategorySerializer, OrderSerializer, OrderItemSerializer,
    MembershipPlanSerializer, MembershipSerializer, CountySerializer, CountyDetailSerializer
)
from ..models.locations import County, Constituency, Ward
from ..serializers import ConstituencySerializer, WardSerializer

User = get_user_model()
logger = logging.getLogger(__name__)

# Authentication Views
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserRegistrationSerializer

class UserDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({
                'error': 'Please provide both email and password'
            }, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(email=email, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            })
        else:
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)

# News Views
class NewsCategoryViewSet(viewsets.ModelViewSet):
    queryset = NewsCategory.objects.all()
    serializer_class = NewsCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class NewsViewSet(viewsets.ModelViewSet):
    queryset = News.objects.filter(is_published=True)
    serializer_class = NewsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category__slug=category)
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class NewsDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

# Event Views
class EventCategoryViewSet(viewsets.ModelViewSet):
    queryset = EventCategory.objects.all()
    serializer_class = EventCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.filter(is_published=True)
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category__slug=category)
        return queryset

class EventRegistrationViewSet(viewsets.ModelViewSet):
    serializer_class = EventRegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return EventRegistration.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# Gallery Views
class GalleryCategoryViewSet(viewsets.ModelViewSet):
    queryset = GalleryCategory.objects.all()
    serializer_class = GalleryCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class GalleryViewSet(viewsets.ModelViewSet):
    queryset = Gallery.objects.all()
    serializer_class = GallerySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category__slug=category)
        return queryset

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)

# Leadership Views
class LeadershipPositionViewSet(viewsets.ModelViewSet):
    queryset = LeadershipPosition.objects.all()
    serializer_class = LeadershipPositionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class NationalLeadershipViewSet(viewsets.ModelViewSet):
    queryset = NationalLeadership.objects.filter(is_active=True)
    serializer_class = NationalLeadershipSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        position = self.request.query_params.get('position', None)
        if position:
            queryset = queryset.filter(position__slug=position)
        return queryset

# Donation Views
class DonationViewSet(viewsets.ModelViewSet):
    queryset = Donation.objects.all()
    serializer_class = DonationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save()

# Shop Views
class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category__slug=category)
        return queryset

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]

class MembershipPlanViewSet(viewsets.ModelViewSet):
    queryset = MembershipPlan.objects.filter(is_active=True)
    serializer_class = MembershipPlanSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class MembershipViewSet(viewsets.ModelViewSet):
    serializer_class = MembershipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Membership.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny], url_path='public')
    def create_public(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if serializer.validated_data.get('membership_type') != 'mwananchi':
            return Response(
                {'detail': 'Paid memberships must be completed through Paystack checkout.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        membership = serializer.save(payment_status='completed', payment_method=None)
        return Response(self.get_serializer(membership).data, status=status.HTTP_201_CREATED)

    @action(
        detail=False,
        methods=['post'],
        permission_classes=[permissions.AllowAny],
        url_path='verify-payment',
    )
    def verify_payment(self, request):
        secret_key = settings.PAYSTACK_SECRET_KEY
        if not secret_key:
            return Response(
                {'detail': 'Paystack payments are not configured.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        reference = request.data.get('reference')
        membership_data = request.data.get('membership')
        if not isinstance(reference, str) or not reference.strip() or len(reference) > 100:
            return Response(
                {'detail': 'A valid Paystack transaction reference is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not isinstance(membership_data, dict):
            return Response(
                {'detail': 'Membership application details are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = MembershipSerializer(data=membership_data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        membership_type = validated_data.get('membership_type')
        expected_amount = Membership.MEMBERSHIP_AMOUNTS.get(membership_type)
        email = validated_data.get('email')
        if not expected_amount or not email:
            return Response(
                {'detail': 'A paid membership type and valid email are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        reference = reference.strip()
        existing_membership = Membership.objects.filter(transaction_id=reference).first()
        if existing_membership:
            if (
                existing_membership.email
                and existing_membership.email.casefold() == email.casefold()
                and existing_membership.membership_type == membership_type
            ):
                return Response(self.get_serializer(existing_membership).data)
            return Response(
                {'detail': 'This Paystack transaction has already been applied.'},
                status=status.HTTP_409_CONFLICT,
            )

        verification_request = Request(
            f'https://api.paystack.co/transaction/verify/{quote(reference, safe="")}',
            headers={
                'Authorization': f'Bearer {secret_key}',
                'Accept': 'application/json',
            },
        )
        try:
            with urlopen(verification_request, timeout=20) as response:
                verification = json.loads(response.read())
        except HTTPError as error:
            logger.warning('Paystack rejected transaction verification with HTTP %s.', error.code)
            return Response(
                {'detail': 'Paystack could not verify this transaction reference.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except (URLError, TimeoutError):
            logger.exception('Could not reach Paystack to verify a membership payment.')
            return Response(
                {'detail': 'Paystack verification is temporarily unavailable. Please retry.'},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        except (json.JSONDecodeError, UnicodeDecodeError):
            logger.exception('Paystack returned an invalid transaction verification response.')
            return Response(
                {'detail': 'Paystack returned an invalid verification response. Please retry.'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        payment = verification.get('data') if isinstance(verification, dict) else None
        customer = payment.get('customer') if isinstance(payment, dict) else None
        if (
            not isinstance(verification, dict)
            or not verification.get('status')
            or not isinstance(payment, dict)
            or payment.get('status') != 'success'
            or payment.get('reference') != reference
            or payment.get('currency') != 'KES'
            or payment.get('amount') != int(expected_amount * 100)
            or not isinstance(customer, dict)
            or (customer.get('email') or '').casefold() != email.casefold()
        ):
            return Response(
                {'detail': 'The Paystack payment could not be confirmed for this membership.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                membership = serializer.save(
                    payment_status='completed',
                    payment_method='paystack',
                    transaction_id=reference,
                )
        except IntegrityError:
            existing_membership = Membership.objects.filter(transaction_id=reference).first()
            if existing_membership:
                return Response(self.get_serializer(existing_membership).data)
            raise

        return Response(self.get_serializer(membership).data, status=status.HTTP_201_CREATED)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

class CountyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = County.objects.all().order_by('name')
    serializer_class = CountySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None  # Disable pagination for counties since there are only 47

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CountyDetailSerializer
        return CountySerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        # Add select_related to optimize the query
        if self.action == 'retrieve':
            return queryset.prefetch_related('constituencies')
        return queryset

class ConstituencyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Constituency.objects.all().order_by('name')  # Default queryset
    serializer_class = ConstituencySerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        county_id = self.request.query_params.get('county', None)
        if county_id:
            return self.queryset.filter(county_id=county_id)
        return self.queryset

class WardViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ward.objects.all().order_by('name')  # Default queryset
    serializer_class = WardSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        constituency_id = self.request.query_params.get('constituency', None)
        if constituency_id:
            return self.queryset.filter(constituency_id=constituency_id)
        return self.queryset 