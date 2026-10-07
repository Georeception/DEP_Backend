from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from ..models.newsletter import NewsletterSubscription
from ..services.email_service import EmailService
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([AllowAny])
def subscribe(request):
    """
    Handle newsletter subscription
    """
    email = request.data.get('email')
    
    if not email:
        return Response(
            {'error': 'Email is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if email already exists
    if NewsletterSubscription.objects.filter(email=email).exists():
        return Response(
            {'error': 'Email already subscribed'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create new subscription
    subscriber = NewsletterSubscription.objects.create(email=email)
    
    # Send verification email
    EmailService.send_verification_email(subscriber)
    
    return Response(
        {'message': 'Subscription successful. Please check your email to verify your subscription.'},
        status=status.HTTP_201_CREATED
    )

@api_view(['GET'])
@permission_classes([AllowAny])
def verify_subscription(request, token):
    """
    Verify newsletter subscription
    """
    try:
        # Log the token for debugging
        logger.info(f"Attempting to verify subscription with token: {token}")
        
        # Try to find the subscription
        subscriber = NewsletterSubscription.objects.get(verification_token=token)
        logger.info(f"Found subscription for email: {subscriber.email}")
        
        if subscriber.is_verified:
            logger.info(f"Email {subscriber.email} is already verified")
            return Response(
                {'message': 'Email already verified'},
                status=status.HTTP_200_OK
            )
        
        # Update subscription
        subscriber.is_verified = True
        subscriber.status = 'active'
        subscriber.verification_token = None  # Clear the token after verification
        subscriber.save()
        
        logger.info(f"Successfully verified email: {subscriber.email}")
        return Response(
            {'message': 'Email verified successfully'},
            status=status.HTTP_200_OK
        )
        
    except NewsletterSubscription.DoesNotExist:
        logger.error(f"No subscription found for token: {token}")
        return Response(
            {'error': 'Invalid or expired verification token'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error verifying subscription: {str(e)}")
        return Response(
            {'error': 'An error occurred while verifying your subscription'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def unsubscribe(request):
    """
    Handle newsletter unsubscription
    """
    email = request.data.get('email')
    
    if not email:
        return Response(
            {'error': 'Email is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    subscriber = get_object_or_404(NewsletterSubscription, email=email)
    subscriber.status = 'inactive'
    subscriber.save()
    
    return Response(
        {'message': 'Successfully unsubscribed'},
        status=status.HTTP_200_OK
    ) 