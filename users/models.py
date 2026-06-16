from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models import Country, Institution


class UserProfile(models.Model):
    """
    Extended user profile for AUDA-NEPAD Genome Editing Portal
    """
    USER_TYPE_CHOICES = [
        ('researcher', 'Researcher / Scientist'),
        ('regulator', 'Regulatory Official'),
        ('policymaker', 'Policy Maker'),
        ('student', 'Student / Trainee'),
        ('private_sector', 'Private Sector'),
        ('cso', 'Civil Society Organization'),
        ('media', 'Media / Journalist'),
        ('general', 'General Public'),
    ]
    
    EXPERIENCE_LEVEL_CHOICES = [
        ('entry', 'Entry Level (< 2 years)'),
        ('mid', 'Mid Level (2-5 years)'),
        ('senior', 'Senior Level (5-10 years)'),
        ('expert', 'Expert Level (10+ years)'),
    ]
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile'
    )
    user_type = models.CharField(
        max_length=20, 
        choices=USER_TYPE_CHOICES, 
        default='general'
    )
    experience_level = models.CharField(
        max_length=20, 
        choices=EXPERIENCE_LEVEL_CHOICES, 
        blank=True, 
        null=True
    )
    institution = models.ForeignKey(
        Institution, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='users'
    )
    country = models.ForeignKey(
        Country, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='users'
    )
    phone = models.CharField(max_length=50, blank=True)
    bio = models.TextField(blank=True, max_length=1000)
    profile_picture = models.ImageField(
        upload_to='profile_pictures/', 
        blank=True, 
        null=True
    )
    
    # Preferences
    newsletter_subscribed = models.BooleanField(default=False)
    notification_email = models.BooleanField(default=True)
    
    # Expertise areas (JSON list of interests)
    areas_of_interest = models.JSONField(default=list, blank=True)
    
    # Verification status
    is_verified = models.BooleanField(default=False)
    verification_document = models.FileField(
        upload_to='verification_docs/', 
        blank=True, 
        null=True
    )
    
    # Social links
    linkedin_url = models.URLField(blank=True)
    researchgate_url = models.URLField(blank=True)
    orcid_id = models.CharField(max_length=50, blank=True)
    
    # Activity tracking
    last_active = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_user_type_display()})"
    
    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username
    
    @property
    def email(self):
        return self.user.email


class SavedItem(models.Model):
    """
    Allows users to save/bookmark items of interest
    """
    ITEM_TYPE_CHOICES = [
        ('publication', 'Publication'),
        ('protocol', 'Protocol'),
        ('project', 'Project'),
        ('expert', 'Expert'),
        ('news', 'News Article'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='saved_items'
    )
    item_type = models.CharField(max_length=20, choices=ITEM_TYPE_CHOICES)
    item_id = models.IntegerField()
    saved_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['user', 'item_type', 'item_id']
        ordering = ['-saved_at']
    
    def __str__(self):
        return f"{self.user.username} saved {self.item_type} #{self.item_id}"


class UserActivityLog(models.Model):
    """
    Track user activities for analytics and personalization
    """
    ACTION_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('view', 'View'),
        ('download', 'Download'),
        ('search', 'Search'),
        ('filter', 'Apply Filter'),
        ('save', 'Save Item'),
        ('share', 'Share'),
        ('comment', 'Comment'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='activities',
        null=True,
        blank=True
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    content_type = models.CharField(max_length=50, blank=True)  # e.g., 'publication', 'project'
    content_id = models.IntegerField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'action', 'created_at']),
            models.Index(fields=['content_type', 'content_id']),
        ]
    
    def __str__(self):
        return f"{self.user} - {self.action} - {self.created_at}"


class NewsletterSubscription(models.Model):
    """
    Independent newsletter subscription (allows non-authenticated users)
    """
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=200, blank=True)
    country = models.ForeignKey(
        Country, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    unsubscribed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-subscribed_at']
    
    def __str__(self):
        return self.email


class PasswordResetRequest(models.Model):
    """
    Track password reset requests
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reset_requests')
    token = models.CharField(max_length=255, unique=True)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    def is_valid(self):
        from django.utils import timezone
        return not self.is_used and self.expires_at > timezone.now()
    
    def __str__(self):
        return f"Reset for {self.user.email} - {'Used' if self.is_used else 'Active'}"