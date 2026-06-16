from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from import_export.admin import ExportActionMixin
from .models import (
    UserProfile, SavedItem, UserActivityLog, 
    NewsletterSubscription, PasswordResetRequest
)


class UserProfileInline(admin.StackedInline):
    """Inline editor for UserProfile within User admin"""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fieldsets = (
        ('User Type & Role', {
            'fields': ('user_type', 'experience_level', 'is_verified')
        }),
        ('Professional Information', {
            'fields': ('institution', 'country', 'bio', 'areas_of_interest')
        }),
        ('Contact Information', {
            'fields': ('phone', 'linkedin_url', 'researchgate_url', 'orcid_id')
        }),
        ('Preferences', {
            'fields': ('newsletter_subscribed', 'notification_email')
        }),
        ('Media', {
            'fields': ('profile_picture', 'verification_document'),
            'classes': ('collapse',)
        }),
    )


# Unregister the default User admin first
admin.site.unregister(User)


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    """Custom User admin with profile integration"""
    inlines = [UserProfileInline]
    list_display = ['username', 'email', 'first_name', 'last_name', 'get_user_type', 'is_active', 'date_joined']
    list_filter = ['is_staff', 'is_active', 'is_superuser', 'profile__user_type', 'profile__is_verified']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'profile__phone']
    
    def get_user_type(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.get_user_type_display()
        return 'Not set'
    get_user_type.short_description = 'User Type'
    get_user_type.admin_order_field = 'profile__user_type'


@admin.register(UserProfile)
class UserProfileAdmin(ExportActionMixin, admin.ModelAdmin):
    """Admin configuration for UserProfile model"""
    list_display = [
        'user_link', 'user_type', 'experience_level', 'country', 
        'institution', 'is_verified', 'newsletter_subscribed', 'last_active'
    ]
    list_filter = [
        'user_type', 'experience_level', 'is_verified', 'newsletter_subscribed',
        'notification_email', 'country'
    ]
    search_fields = [
        'user__username', 'user__email', 'user__first_name', 'user__last_name',
        'phone', 'institution__name', 'bio'
    ]
    readonly_fields = ['created_at', 'updated_at', 'last_active', 'user_link']
    list_editable = ['is_verified', 'newsletter_subscribed']
    
    fieldsets = (
        ('User Account', {
            'fields': ('user_link', 'user_type', 'experience_level')
        }),
        ('Professional Information', {
            'fields': ('institution', 'country', 'bio', 'areas_of_interest')
        }),
        ('Contact Details', {
            'fields': ('phone', 'email_display', 'linkedin_url', 'researchgate_url', 'orcid_id')
        }),
        ('Verification Status', {
            'fields': ('is_verified', 'verification_document', 'verification_status_badge')
        }),
        ('Preferences', {
            'fields': ('newsletter_subscribed', 'notification_email')
        }),
        ('Media', {
            'fields': ('profile_picture_preview', 'profile_picture'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_active'),
            'classes': ('collapse',)
        }),
    )
    
    def user_link(self, obj):
        """Display user link to admin change page"""
        url = reverse('admin:auth_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = 'User'
    
    def email_display(self, obj):
        """Display user email"""
        return obj.user.email
    email_display.short_description = 'Email'
    
    def profile_picture_preview(self, obj):
        """Display profile picture thumbnail"""
        if obj.profile_picture:
            return format_html(
                '<img src="{}" style="max-width: 100px; max-height: 100px; border-radius: 50%;" />',
                obj.profile_picture.url
            )
        return format_html(
            '<div style="width: 100px; height: 100px; background: #e0e0e0; border-radius: 50%; display: flex; align-items: center; justify-content: center;">'
            '<span style="color: #666;">No Image</span></div>'
        )
    profile_picture_preview.short_description = 'Profile Picture'
    
    def verification_status_badge(self, obj):
        """Display verification status as colored badge"""
        if obj.is_verified:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 3px 10px; border-radius: 20px;">✓ Verified</span>'
            )
        else:
            return format_html(
                '<span style="background: #dc3545; color: white; padding: 3px 10px; border-radius: 20px;">✗ Not Verified</span>'
            )
    verification_status_badge.short_description = 'Verification'
    
    actions = ['verify_selected', 'unverify_selected']
    
    def verify_selected(self, request, queryset):
        """Bulk verify selected profiles"""
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} profile(s) have been verified.')
    verify_selected.short_description = 'Verify selected profiles'
    
    def unverify_selected(self, request, queryset):
        """Bulk unverify selected profiles"""
        updated = queryset.update(is_verified=False)
        self.message_user(request, f'{updated} profile(s) have been unverified.')
    unverify_selected.short_description = 'Unverify selected profiles'


@admin.register(SavedItem)
class SavedItemAdmin(admin.ModelAdmin):
    """Admin configuration for SavedItem model"""
    list_display = ['user', 'item_type', 'item_id', 'saved_at']
    list_filter = ['item_type', 'saved_at']
    search_fields = ['user__username', 'user__email', 'notes']
    readonly_fields = ['saved_at']
    date_hierarchy = 'saved_at'


@admin.register(UserActivityLog)
class UserActivityLogAdmin(admin.ModelAdmin):
    """Admin configuration for UserActivityLog model"""
    list_display = ['user', 'action', 'content_type', 'created_at']
    list_filter = ['action', 'content_type', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'ip_address', 'user_agent']
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(ExportActionMixin, admin.ModelAdmin):
    """Admin configuration for NewsletterSubscription model"""
    list_display = ['email', 'name', 'country', 'is_active', 'subscribed_at']
    list_filter = ['is_active', 'country', 'subscribed_at']
    search_fields = ['email', 'name']
    readonly_fields = ['subscribed_at', 'unsubscribed_at']
    date_hierarchy = 'subscribed_at'
    
    actions = ['activate_subscribers', 'deactivate_subscribers']
    
    def activate_subscribers(self, request, queryset):
        """Bulk activate newsletter subscribers"""
        updated = queryset.update(is_active=True, unsubscribed_at=None)
        self.message_user(request, f'{updated} subscriber(s) have been activated.')
    activate_subscribers.short_description = 'Activate selected subscribers'
    
    def deactivate_subscribers(self, request, queryset):
        """Bulk deactivate newsletter subscribers"""
        from django.utils import timezone
        updated = queryset.update(is_active=False, unsubscribed_at=timezone.now())
        self.message_user(request, f'{updated} subscriber(s) have been deactivated.')
    deactivate_subscribers.short_description = 'Deactivate selected subscribers'


@admin.register(PasswordResetRequest)
class PasswordResetRequestAdmin(admin.ModelAdmin):
    """Admin configuration for PasswordResetRequest model"""
    list_display = ['user', 'is_used', 'is_valid_display', 'expires_at', 'created_at']
    list_filter = ['is_used', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['token', 'expires_at', 'created_at']
    
    def is_valid_display(self, obj):
        """Display whether token is still valid"""
        from django.utils import timezone
        if obj.is_used:
            return format_html('<span style="color: #dc3545;">Used</span>')
        elif obj.expires_at < timezone.now():
            return format_html('<span style="color: #ffc107;">Expired</span>')
        else:
            return format_html('<span style="color: #28a745;">Valid</span>')
    is_valid_display.short_description = 'Status'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False