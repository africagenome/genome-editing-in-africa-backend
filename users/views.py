from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
import secrets
from datetime import timedelta

from .models import (
    UserProfile, SavedItem, UserActivityLog, 
    NewsletterSubscription, PasswordResetRequest
)
from .serializers import (
    RegisterSerializer, UserSerializer, UserProfileSerializer,
    UserProfileUpdateSerializer, ChangePasswordSerializer,
    ForgotPasswordSerializer, ResetPasswordSerializer,
    SavedItemSerializer, NewsletterSubscriptionSerializer,
    UserActivityLogSerializer, ProfileVerificationSerializer
)


class RegisterView(generics.CreateAPIView):
    """
    User registration endpoint
    """
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        refresh = RefreshToken.for_user(user)
        
        # Log activity
        self._log_activity(user, 'register')
        
        return Response({
            'user': UserSerializer(user).data,
            'profile': UserProfileSerializer(user.profile).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)
    
    def _log_activity(self, user, action):
        """Helper to log user activity"""
        try:
            UserActivityLog.objects.create(
                user=user,
                action=action,
                ip_address=self.request.META.get('REMOTE_ADDR', ''),
                user_agent=self.request.META.get('HTTP_USER_AGENT', '')[:500]
            )
        except Exception:
            pass


class LoginView(APIView):
    """
    User login endpoint (JWT)
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({
                'error': 'Please provide both username and password'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(username=username, password=password)
        
        if user is None:
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.is_active:
            return Response({
                'error': 'Account is disabled'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        refresh = RefreshToken.for_user(user)
        
        # Update last active
        user.profile.last_active = timezone.now()
        user.profile.save(update_fields=['last_active'])
        
        # Log activity
        self._log_activity(user, 'login', request)
        
        return Response({
            'user': UserSerializer(user).data,
            'profile': UserProfileSerializer(user.profile).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
    
    def _log_activity(self, user, action, request):
        try:
            UserActivityLog.objects.create(
                user=user,
                action=action,
                ip_address=request.META.get('REMOTE_ADDR', ''),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
            )
        except Exception:
            pass


class LogoutView(APIView):
    """
    User logout endpoint (blacklists refresh token)
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            # Log activity
            UserActivityLog.objects.create(
                user=request.user,
                action='logout',
                ip_address=request.META.get('REMOTE_ADDR', ''),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
            )
            
            return Response({'message': 'Successfully logged out'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    Get and update user profile
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserProfileUpdateSerializer
    
    def get_object(self):
        return self.request.user.profile
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserProfileSerializer
        return UserProfileUpdateSerializer
    
    def perform_update(self, serializer):
        serializer.save()
        UserActivityLog.objects.create(
            user=self.request.user,
            action='update_profile',
            ip_address=self.request.META.get('REMOTE_ADDR', ''),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')[:500]
        )


class ChangePasswordView(APIView):
    """
    Change user password
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        
        # Check old password
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({
                'old_password': 'Wrong password'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Set new password
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        # Log activity
        UserActivityLog.objects.create(
            user=user,
            action='change_password',
            ip_address=request.META.get('REMOTE_ADDR', ''),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
        )
        
        return Response({'message': 'Password changed successfully'})


class ForgotPasswordView(APIView):
    """
    Request password reset
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        user = User.objects.get(email=email)
        
        # Generate reset token
        token = secrets.token_urlsafe(32)
        expires_at = timezone.now() + timedelta(hours=24)
        
        # Save reset request
        reset_request = PasswordResetRequest.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )
        
        # Send email (in production, use Celery for async)
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        
        try:
            send_mail(
                subject='Password Reset Request - AUDA-NEPAD Genome Editing Portal',
                message=f"""
                Hello {user.get_full_name() or user.username},
                
                You requested to reset your password for the AUDA-NEPAD Genome Editing Portal.
                
                Click the link below to reset your password (valid for 24 hours):
                {reset_link}
                
                If you did not request this, please ignore this email.
                
                Best regards,
                AUDA-NEPAD Genome Editing Team
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception as e:
            # Log error but don't expose to user
            print(f"Email sending failed: {e}")
        
        return Response({
            'message': 'Password reset link sent to your email address'
        })


class ResetPasswordView(APIView):
    """
    Reset password using token
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        token = serializer.validated_data['token']
        
        try:
            reset_request = PasswordResetRequest.objects.get(token=token)
        except PasswordResetRequest.DoesNotExist:
            return Response({
                'error': 'Invalid or expired token'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not reset_request.is_valid():
            return Response({
                'error': 'Token has expired'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Reset password
        user = reset_request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        # Mark token as used
        reset_request.is_used = True
        reset_request.save()
        
        # Log activity
        UserActivityLog.objects.create(
            user=user,
            action='reset_password',
            ip_address=request.META.get('REMOTE_ADDR', ''),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
        )
        
        return Response({'message': 'Password reset successfully'})


class SavedItemViewSet(viewsets.ModelViewSet):
    """
    Manage saved/bookmarked items
    """
    serializer_class = SavedItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return SavedItem.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        UserActivityLog.objects.create(
            user=self.request.user,
            action='save',
            content_type=serializer.validated_data.get('item_type', ''),
            content_id=serializer.validated_data.get('item_id'),
            ip_address=self.request.META.get('REMOTE_ADDR', ''),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')[:500],
            metadata={'item_type': serializer.validated_data.get('item_type')}
        )
    
    @action(detail=False, methods=['delete'])
    def clear_all(self, request):
        """Delete all saved items for the current user"""
        count = self.get_queryset().delete()[0]
        return Response({'deleted_count': count})


class NewsletterSubscribeView(generics.CreateAPIView):
    """
    Subscribe to newsletter (public endpoint)
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = NewsletterSubscriptionSerializer
    
    def create(self, request, *args, **kwargs):
        email = request.data.get('email')
        
        # Check if already subscribed
        existing = NewsletterSubscription.objects.filter(email=email).first()
        if existing:
            if existing.is_active:
                return Response({
                    'message': 'This email is already subscribed'
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Reactivate
                existing.is_active = True
                existing.unsubscribed_at = None
                existing.save()
                serializer = self.get_serializer(existing)
                return Response(serializer.data)
        
        return super().create(request, *args, **kwargs)


class NewsletterUnsubscribeView(APIView):
    """
    Unsubscribe from newsletter
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        
        try:
            subscription = NewsletterSubscription.objects.get(email=email)
            subscription.is_active = False
            subscription.unsubscribed_at = timezone.now()
            subscription.save()
            return Response({'message': 'Successfully unsubscribed'})
        except NewsletterSubscription.DoesNotExist:
            return Response({'message': 'Email not found in subscription list'}, status=status.HTTP_404_NOT_FOUND)


class UserStatsView(APIView):
    """
    Get user statistics for dashboard
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        stats = {
            'saved_count': SavedItem.objects.filter(user=user).count(),
            'viewed_count': UserActivityLog.objects.filter(
                user=user, action='view'
            ).count(),
            'downloaded_count': UserActivityLog.objects.filter(
                user=user, action='download'
            ).count(),
            'last_active': user.profile.last_active,
            'member_since': user.date_joined,
            'activities_30d': UserActivityLog.objects.filter(
                user=user,
                created_at__gte=timezone.now() - timedelta(days=30)
            ).count(),
        }
        
        return Response(stats)


class ProfileVerificationView(APIView):
    """
    Submit profile verification request
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ProfileVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        profile = request.user.profile
        
        if serializer.validated_data.get('verification_document'):
            profile.verification_document = serializer.validated_data['verification_document']
        
        # Log verification request
        UserActivityLog.objects.create(
            user=request.user,
            action='submit_verification',
            ip_address=request.META.get('REMOTE_ADDR', ''),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            metadata={
                'institution': serializer.validated_data.get('institution'),
                'job_title': serializer.validated_data.get('job_title')
            }
        )
        
        profile.save()
        
        # Notify admins (in production, send email)
        
        return Response({
            'message': 'Verification request submitted successfully. Our team will review your application.'
        })