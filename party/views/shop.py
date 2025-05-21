from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from ..models.shop import Product, Order, OrderItem, ProductCategory, Review
from ..serializers import (
    ProductSerializer, OrderSerializer, OrderItemSerializer,
    ProductCategorySerializer, ReviewSerializer
)

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category__slug=category)
        return queryset.prefetch_related('reviews')

    @action(detail=True, methods=['post'])
    def add_review(self, request, slug=None):
        product = self.get_object()
        user = request.user
        
        # Check if user has already reviewed this product
        existing_review = Review.objects.filter(product=product, user=user).first()
        if existing_review:
            return Response(
                {'error': 'You have already reviewed this product'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(product=product, user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def reviews(self, request, slug=None):
        product = self.get_object()
        reviews = product.reviews.all()
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        order = serializer.save(user=self.request.user)
        
        # Create order items
        items_data = self.request.data.get('items', [])
        for item_data in items_data:
            item_data['order'] = order.id
            item_serializer = OrderItemSerializer(data=item_data)
            if item_serializer.is_valid():
                item_serializer.save()
            else:
                order.delete()
                return Response(
                    item_serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )

    @action(detail=True, methods=['post'])
    def initiate_payment(self, request, pk=None):
        order = self.get_object()
        payment_method = request.data.get('payment_method')
        
        if not payment_method:
            return Response(
                {'error': 'Payment method is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Here you would integrate with your payment provider (e.g., M-PESA)
        # For now, we'll just update the order status
        order.payment_method = payment_method
        order.status = 'processing'
        order.save()
        
        return Response({
            'message': 'Payment initiated',
            'order_id': order.id,
            'status': order.status
        })

    @action(detail=True, methods=['post'])
    def verify_payment(self, request, pk=None):
        order = self.get_object()
        transaction_id = request.data.get('transaction_id')
        
        if not transaction_id:
            return Response(
                {'error': 'Transaction ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Here you would verify the payment with your payment provider
        # For now, we'll just update the order status
        order.transaction_id = transaction_id
        order.payment_status = 'completed'
        order.status = 'processing'
        order.save()
        
        return Response({
            'message': 'Payment verified',
            'order_id': order.id,
            'status': order.status
        }) 