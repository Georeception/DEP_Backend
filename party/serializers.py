from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import (
    User, News, NewsCategory, Event, EventCategory, EventRegistration,
    Gallery, GalleryCategory, NationalLeadership, LeadershipPosition,
    Donation, Product, ProductCategory, Order, OrderItem, Review,
    MembershipPlan, Membership
)
from .models.locations import County, Constituency, Ward
from django.conf import settings
import cloudinary
from .models.shop import PickupLocation

# User Serializers
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'password2', 'first_name', 'last_name', 
                 'phone_number', 'county', 'constituency', 'ward', 'membership_type')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 
                 'phone_number', 'county', 'constituency', 'ward', 'membership_type', 
                 'membership_status', 'profile_picture')
        read_only_fields = ('id', 'membership_status')

# News Serializers
class NewsCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsCategory
        fields = '__all__'

class NewsSerializer(serializers.ModelSerializer):
    category = NewsCategorySerializer(read_only=True)
    author = UserSerializer(read_only=True)
    preview_image_url = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = News
        fields = '__all__'
        read_only_fields = ('author', 'created_at', 'updated_at')

    def get_preview_image_url(self, obj):
        return obj.get_preview_image_url()

    def get_image_url(self, obj):
        return obj.get_image_url()

# Event Serializers
class EventCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EventCategory
        fields = '__all__'

class EventRegistrationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = EventRegistration
        fields = '__all__'
        read_only_fields = ('user', 'registration_date')

class EventSerializer(serializers.ModelSerializer):
    category = EventCategorySerializer(read_only=True)
    registrations = EventRegistrationSerializer(many=True, read_only=True)
    preview_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def get_preview_image_url(self, obj):
        return obj.get_preview_image_url()

# Gallery Serializers
class GalleryCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GalleryCategory
        fields = '__all__'

class GallerySerializer(serializers.ModelSerializer):
    category = GalleryCategorySerializer(read_only=True)
    uploaded_by = UserSerializer(read_only=True)
    image_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Gallery
        fields = '__all__'
        read_only_fields = ('uploaded_by', 'created_at', 'updated_at')

    def get_image_url(self, obj):
        return obj.get_image_url()

    def get_thumbnail_url(self, obj):
        return obj.get_thumbnail_url()

# Leadership Serializers
class LeadershipPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadershipPosition
        fields = ['id', 'title', 'slug', 'description', 'order']

class NationalLeadershipSerializer(serializers.ModelSerializer):
    position = LeadershipPositionSerializer(read_only=True)
    image = serializers.SerializerMethodField()
    
    class Meta:
        model = NationalLeadership
        fields = ['id', 'name', 'position', 'bio', 'image', 'start_date', 'end_date', 'is_active']
    
    def get_image(self, obj):
        if not obj.image:
            return None
        # If it's a full URL, return it as is
        if str(obj.image).startswith('http'):
            return str(obj.image)
        # If it's a Cloudinary public_id (starts with 'v'), return the full URL
        if str(obj.image).startswith('v'):
            return f"https://res.cloudinary.com/{settings.CLOUDINARY_STORAGE['CLOUD_NAME']}/image/upload/{obj.image}"
        # If it's a local path, try to get the Cloudinary URL
        try:
            # Get the Cloudinary URL for the image
            # The public_id should be the path without the version number
            public_id = str(obj.image)
            print(f"Original image path: {public_id}")  # Debug log
            
            # Handle different path formats
            if public_id.startswith('leadership/'):
                # Path already includes leadership folder
                cloudinary_path = public_id
            else:
                # Extract filename and add leadership folder
                filename = public_id.split('/')[-1]
                cloudinary_path = f"leadership/{filename}"
            
            print(f"Cloudinary path: {cloudinary_path}")  # Debug log
            
            # Try to get the image from Cloudinary
            try:
                result = cloudinary.uploader.explicit(cloudinary_path, type="upload")
                print(f"Cloudinary result: {result}")  # Debug log
                return result['secure_url']
            except Exception as e:
                print(f"Error getting Cloudinary URL: {str(e)}")  # Debug log
                # Fallback to basic URL
                return f"https://res.cloudinary.com/{settings.CLOUDINARY_STORAGE['CLOUD_NAME']}/image/upload/{cloudinary_path}"
        except Exception as e:
            print(f"Error in get_image for {obj.name}: {str(e)}")  # Debug log
            # Fallback to local media URL if Cloudinary URL can't be generated
            return f"{settings.MEDIA_URL}{obj.image}"

# Donation Serializers
class DonationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donation
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

# Shop Serializers
class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = ['id', 'user', 'rating', 'comment', 'created_at']
        read_only_fields = ['user', 'created_at']
    
    def get_user(self, obj):
        return obj.user.get_full_name() or obj.user.email

class ProductSerializer(serializers.ModelSerializer):
    category = ProductCategorySerializer(read_only=True)
    original_price = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
    discount = serializers.IntegerField(read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'price', 'original_price',
            'price_modifier_type', 'price_modifier_value', 'discount',
            'image', 'image_url', 'category', 'stock', 'is_featured', 'reviews',
            'average_rating', 'created_at', 'updated_at'
        ]
        read_only_fields = ('created_at', 'updated_at', 'original_price', 'discount')

    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if not reviews:
            return None
        return sum(review.rating for review in reviews) / len(reviews)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['original_price'] = instance.calculate_original_price()
        data['discount'] = instance.calculate_discount()
        return data

    def get_image_url(self, obj):
        if obj.image and str(obj.image).startswith('v'):
            return f"https://res.cloudinary.com/dgkommeq9/image/upload/{obj.image}"
        return obj.image.url if obj.image else None

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

# Membership Serializers
class MembershipPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = MembershipPlan
        fields = '__all__'

class MembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        fields = [
            'id', 'membership_type', 'membership_category', 'payment_status', 'payment_method', 'transaction_id', 'amount',
            'first_name', 'last_name', 'full_name', 'national_id_number', 'date_of_birth',
            'email', 'phone', 'whatsapp_number', 'sub_county', 'postal_address', 'county', 'constituency',
            'ward', 'electoral_county', 'electoral_constituency', 'electoral_ward',
            'dep_bus_membership_status', 'membership_status_confirmed', 'membership_reference',
            'aspirant_details', 'age', 'gender', 'occupation', 'interests', 'created_at'
        ]
        read_only_fields = ['payment_status', 'payment_method', 'transaction_id', 'amount', 'created_at']

    def validate(self, attrs):
        membership_type = attrs.get('membership_type')
        membership_category = attrs.get('membership_category', 'general')
        if membership_type == 'mwananchi' and membership_category != 'general':
            raise serializers.ValidationError({
                'membership_category': 'Mwananchi is only available under General membership.'
            })
        if Membership.get_amount(membership_type, membership_category) is None:
            raise serializers.ValidationError({
                'membership_category': 'This membership plan is not available in the selected category.'
            })
        if membership_type in {
            'mca', 'mp', 'women_rep', 'senator', 'governor',
        }:
            if not attrs.get('membership_reference', '').strip():
                raise serializers.ValidationError({
                    'membership_reference': 'A DEP-BUS membership number/reference is required for aspirant applications.'
                })
            if not attrs.get('dep_bus_membership_status'):
                raise serializers.ValidationError({
                    'dep_bus_membership_status': 'Please answer whether you are currently a DEP-BUS member.'
                })
            if attrs.get('membership_status_confirmed') is None:
                raise serializers.ValidationError({
                    'membership_status_confirmed': 'Please confirm whether you checked your membership using USSD *509#.'
                })
            if not isinstance(attrs.get('aspirant_details', {}), dict):
                raise serializers.ValidationError({
                    'aspirant_details': 'Aspirant application details must be an object.'
                })
            if not all(attrs.get(field) for field in ('county', 'constituency', 'ward')):
                raise serializers.ValidationError({
                    'ward': 'Select your county of residence, constituency and ward.'
                })
            if not all(attrs.get(field) for field in (
                'electoral_county', 'electoral_constituency', 'electoral_ward',
            )):
                raise serializers.ValidationError({
                    'electoral_ward': 'Select an electoral county, constituency and ward.'
                })
            county = attrs.get('county')
            constituency = attrs.get('constituency')
            ward = attrs.get('ward')
            if constituency.county_id != county.id:
                raise serializers.ValidationError({
                    'constituency': 'Select a constituency in the selected county of residence.'
                })
            if ward.constituency_id != constituency.id:
                raise serializers.ValidationError({
                    'ward': 'Select a ward in the selected constituency of residence.'
                })
            electoral_county = attrs.get('electoral_county')
            electoral_constituency = attrs.get('electoral_constituency')
            electoral_ward = attrs.get('electoral_ward')
            if electoral_county and electoral_constituency and electoral_constituency.county_id != electoral_county.id:
                raise serializers.ValidationError({
                    'electoral_constituency': 'Select a constituency in the selected electoral county.'
                })
            if electoral_constituency and electoral_ward and electoral_ward.constituency_id != electoral_constituency.id:
                raise serializers.ValidationError({
                    'electoral_ward': 'Select a ward in the selected electoral constituency.'
                })
        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user

        membership_type = validated_data.get('membership_type')
        membership_category = validated_data.get('membership_category', 'general')
        validated_data.setdefault(
            'amount',
            Membership.get_amount(membership_type, membership_category),
        )

        # For Mwananchi memberships, automatically set as completed
        if membership_type == 'mwananchi':
            validated_data['payment_status'] = 'completed'
        
        return super().create(validated_data)

class WardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ward
        fields = ['id', 'name', 'code']

class ConstituencySerializer(serializers.ModelSerializer):
    wards = WardSerializer(many=True, read_only=True)
    
    class Meta:
        model = Constituency
        fields = ['id', 'name', 'code', 'wards']

class CountySerializer(serializers.ModelSerializer):
    class Meta:
        model = County
        fields = ['id', 'name', 'code', 'country']

class CountyDetailSerializer(serializers.ModelSerializer):
    constituencies = ConstituencySerializer(many=True, read_only=True)
    
    class Meta:
        model = County
        fields = ['id', 'name', 'code', 'country', 'constituencies']

class PickupLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PickupLocation
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at'] 