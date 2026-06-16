from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.validators import EmailValidator
from .models import (
    UserProfile, SavedItem, UserActivityLog, 
    NewsletterSubscription, PasswordResetRequest
)
from core.models import Country, Institution


class UserSerializer(serializers.ModelSerializer):
    """
    Basic User serializer
    """
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name']
        read_only_fields = ['id']
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Complete User Profile serializer
    """
    user = UserSerializer(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    country_name = serializers.CharField(source='country.name', read_only=True)
    institution_name = serializers.CharField(source='institution.name', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'username', 'email', 'user_type', 'experience_level',
            'institution', 'institution_name', 'country', 'country_name',
            'phone', 'bio', 'profile_picture', 'newsletter_subscribed',
            'notification_email', 'areas_of_interest', 'is_verified',
            'linkedin_url', 'researchgate_url', 'orcid_id',
            'last_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['is_verified', 'last_active', 'created_at', 'updated_at']


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile (write operations)
    """
    class Meta:
        model = UserProfile
        fields = [
            'user_type', 'experience_level', 'institution', 'country',
            'phone', 'bio', 'profile_picture', 'newsletter_subscribed',
            'notification_email', 'areas_of_interest', 'linkedin_url',
            'researchgate_url', 'orcid_id'
        ]


class RegisterSerializer(serializers.ModelSerializer):
    """
    User registration serializer with password validation
    """
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(
        required=True,
        validators=[EmailValidator()]
    )
    user_type = serializers.ChoiceField(
        choices=UserProfile.USER_TYPE_CHOICES,
        write_only=True
    )
    
    class Meta:
        model = User
        fields = ['username', 'password', 'password2', 'email', 
                  'first_name', 'last_name', 'user_type']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        
        # Check if email already exists
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError(
                {"email": "A user with this email already exists."}
            )
        
        return attrs
    
    def create(self, validated_data):
        user_type = validated_data.pop('user_type')
        validated_data.pop('password2')
        
        user = User.objects.create_user(**validated_data)
        
        UserProfile.objects.create(
            user=user,
            user_type=user_type
        )
        
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    confirm_password = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError(
                {"confirm_password": "New passwords do not match."}
            )
        return attrs


class ForgotPasswordSerializer(serializers.Serializer):
    """
    Serializer for password reset request
    """
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "No user found with this email address."
            )
        return value


class ResetPasswordSerializer(serializers.Serializer):
    """
    Serializer for password reset confirmation
    """
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    confirm_password = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )
        return attrs


class SavedItemSerializer(serializers.ModelSerializer):
    """
    Serializer for saved/bookmarked items
    """
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = SavedItem
        fields = ['id', 'item_type', 'item_id', 'saved_at', 'notes']
        read_only_fields = ['id', 'saved_at']


class NewsletterSubscriptionSerializer(serializers.ModelSerializer):
    """
    Serializer for newsletter subscription
    """
    country_name = serializers.CharField(source='country.name', read_only=True)
    
    class Meta:
        model = NewsletterSubscription
        fields = ['id', 'email', 'name', 'country', 'country_name', 
                  'is_active', 'subscribed_at']
        read_only_fields = ['id', 'subscribed_at', 'is_active']


class UserActivityLogSerializer(serializers.ModelSerializer):
    """
    Serializer for user activity logs
    """
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserActivityLog
        fields = ['id', 'user', 'action', 'content_type', 'content_id',
                  'ip_address', 'user_agent', 'metadata', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserStatsSerializer(serializers.Serializer):
    """
    Serializer for user statistics (dashboard)
    """
    saved_count = serializers.IntegerField()
    viewed_count = serializers.IntegerField()
    downloaded_count = serializers.IntegerField()
    last_active = serializers.DateTimeField()


class ProfileVerificationSerializer(serializers.Serializer):
    """
    Serializer for profile verification submission
    """
    verification_document = serializers.FileField(required=True)
    institution = serializers.IntegerField(required=False)
    job_title = serializers.CharField(required=False)