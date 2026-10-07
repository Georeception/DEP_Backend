from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import (
    User, News, NewsCategory, Event, EventCategory, EventRegistration,
    Gallery, GalleryCategory, NationalLeadership, LeadershipPosition,
    Donation, Product, ProductCategory, Order, OrderItem,
    MembershipPlan, Membership, NewsletterSubscription
)
from .models.locations import County, Constituency, Ward
from .models.shop import PickupLocation

# Location Admin
@admin.register(County)
class CountyAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')
    ordering = ('name',)

@admin.register(Constituency)
class ConstituencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'county')
    list_filter = ('county',)
    search_fields = ('name', 'code', 'county__name')
    ordering = ('county', 'name')

@admin.register(Ward)
class WardAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'constituency', 'get_county')
    list_filter = ('constituency__county', 'constituency')
    search_fields = ('name', 'code', 'constituency__name', 'constituency__county__name')
    ordering = ('constituency__county', 'constituency', 'name')

    def get_county(self, obj):
        return obj.constituency.county.name
    get_county.short_description = 'County'
    get_county.admin_order_field = 'constituency__county__name'

# User Admin
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'phone_number', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'phone_number')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'phone_number'),
        }),
    )

# News Admin
@admin.register(NewsCategory)
class NewsCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',)
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'is_published', 'created_at',)
    list_filter = ('is_published', 'category', 'created_at',)
    search_fields = ('title', 'content',)
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'

# Event Admin
@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',)
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'start_date', 'end_date', 'is_published',)
    list_filter = ('is_published', 'category', 'start_date',)
    search_fields = ('title', 'description',)
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'start_date'

@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'registration_date', 'status',)
    list_filter = ('status', 'registration_date',)
    search_fields = ('user__email', 'event__title',)
    date_hierarchy = 'registration_date'

# Gallery Admin
@admin.register(GalleryCategory)
class GalleryCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',)
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'uploaded_by', 'created_at',)
    list_filter = ('category', 'created_at',)
    search_fields = ('title', 'description',)
    date_hierarchy = 'created_at'

# Leadership Admin
@admin.register(LeadershipPosition)
class LeadershipPositionAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'order',)
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title',)
    ordering = ('order',)

@admin.register(NationalLeadership)
class NationalLeadershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'position', 'start_date', 'end_date', 'is_active',)
    list_filter = ('is_active', 'position', 'start_date',)
    search_fields = ('user__email', 'position__title',)
    date_hierarchy = 'start_date'

# Donation Admin
@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('donor_name', 'amount', 'payment_method', 'status', 'created_at',)
    list_filter = ('status', 'payment_method', 'created_at',)
    search_fields = ('donor_name', 'donor_email', 'transaction_id',)
    date_hierarchy = 'created_at'

# Shop Admin
@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',)
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'is_featured',)
    list_filter = ('is_featured', 'category',)
    search_fields = ('name', 'description',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'status', 'total_amount', 'created_at',)
    list_filter = ('status', 'created_at',)
    search_fields = ('order_number', 'user__email',)
    date_hierarchy = 'created_at'

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price',)
    list_filter = ('order__status',)
    search_fields = ('order__order_number', 'product__name',)

# Membership Admin
@admin.register(MembershipPlan)
class MembershipPlanAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'amount', 'is_active',)
    list_filter = ('is_active', 'type',)
    search_fields = ('title', 'description',)

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('get_member_name', 'membership_type', 'payment_status', 'payment_method', 'amount', 'created_at')
    list_filter = ('membership_type', 'payment_status', 'payment_method', 'created_at')
    search_fields = ('user__email', 'email', 'first_name', 'last_name', 'phone')
    date_hierarchy = 'created_at'
    
    def get_member_name(self, obj):
        if obj.user:
            return f"{obj.user.get_full_name()} ({obj.user.email})"
        return f"{obj.first_name} {obj.last_name} ({obj.email})"
    get_member_name.short_description = 'Member'

@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscription_date', 'status', 'is_verified', 'last_updated')
    list_filter = ('status', 'is_verified', 'subscription_date')
    search_fields = ('email',)
    date_hierarchy = 'subscription_date'
    readonly_fields = ('subscription_date', 'last_updated')
    fieldsets = (
        (None, {
            'fields': ('email', 'status', 'is_verified')
        }),
        ('Verification', {
            'fields': ('verification_token',)
        }),
        ('Timestamps', {
            'fields': ('subscription_date', 'last_updated'),
            'classes': ('collapse',)
        }),
    )

@admin.register(PickupLocation)
class PickupLocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'state', 'phone', 'email', 'is_active')
    list_filter = ('is_active', 'city', 'state')
    search_fields = ('name', 'address', 'city', 'state', 'phone', 'email')
    ordering = ('city', 'name')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'is_active')
        }),
        ('Location Details', {
            'fields': ('address', 'city', 'state', 'zip_code')
        }),
        ('Contact Information', {
            'fields': ('phone', 'email')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
