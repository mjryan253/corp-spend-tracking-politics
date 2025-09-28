"""
Authentication and authorization system for the Corporate Spending Tracker.
Provides JWT-based authentication with role-based access control.
"""
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db import models
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class UserProfile(models.Model):
    """Extended user profile with additional fields."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=50, choices=[
        ('admin', 'Administrator'),
        ('analyst', 'Data Analyst'),
        ('viewer', 'Viewer'),
        ('api_user', 'API User')
    ], default='viewer')
    organization = models.CharField(max_length=255, blank=True, null=True)
    api_key = models.CharField(max_length=64, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} ({self.role})"


class AuthenticationSystem:
    """
    Comprehensive authentication system with JWT tokens and role-based access.
    """
    
    @staticmethod
    def create_user_token(user: User) -> Dict[str, str]:
        """
        Create JWT token for user.
        
        Args:
            user: User object
            
        Returns:
            Dictionary with access and refresh tokens
        """
        try:
            refresh = RefreshToken.for_user(user)
            return {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user_id': user.id,
                'username': user.username,
                'role': getattr(user.profile, 'role', 'viewer') if hasattr(user, 'profile') else 'viewer'
            }
        except Exception as e:
            logger.error(f"Error creating token for user {user.username}: {e}")
            raise
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate user and return token.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            Authentication result with token or None
        """
        try:
            user = authenticate(username=username, password=password)
            if user and user.is_active:
                token_data = AuthenticationSystem.create_user_token(user)
                return {
                    'success': True,
                    'token': token_data,
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'role': getattr(user.profile, 'role', 'viewer') if hasattr(user, 'profile') else 'viewer'
                    }
                }
        except Exception as e:
            logger.error(f"Authentication error for user {username}: {e}")
        
        return None
    
    @staticmethod
    def create_user(username: str, email: str, password: str, 
                   role: str = 'viewer', organization: str = None) -> Optional[User]:
        """
        Create new user with profile.
        
        Args:
            username: Username
            email: Email address
            password: Password
            role: User role
            organization: Organization name
            
        Returns:
            Created user or None
        """
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            
            # Create profile
            UserProfile.objects.create(
                user=user,
                role=role,
                organization=organization
            )
            
            logger.info(f"Created user {username} with role {role}")
            return user
            
        except Exception as e:
            logger.error(f"Error creating user {username}: {e}")
            return None
    
    @staticmethod
    def get_user_permissions(user: User) -> List[str]:
        """
        Get user permissions based on role.
        
        Args:
            user: User object
            
        Returns:
            List of permission strings
        """
        if not hasattr(user, 'profile'):
            return ['view']
        
        role_permissions = {
            'admin': [
                'view', 'create', 'update', 'delete', 'manage_users',
                'view_analytics', 'manage_data', 'export_data'
            ],
            'analyst': [
                'view', 'view_analytics', 'export_data', 'manage_data'
            ],
            'api_user': [
                'view', 'api_access'
            ],
            'viewer': [
                'view'
            ]
        }
        
        return role_permissions.get(user.profile.role, ['view'])


class RoleBasedPermission(BasePermission):
    """
    Custom permission class for role-based access control.
    """
    
    def __init__(self, required_permissions: List[str]):
        self.required_permissions = required_permissions
    
    def has_permission(self, request, view):
        """
        Check if user has required permissions.
        
        Args:
            request: HTTP request
            view: View being accessed
            
        Returns:
            True if user has permission, False otherwise
        """
        if not request.user or not request.user.is_authenticated:
            return False
        
        user_permissions = AuthenticationSystem.get_user_permissions(request.user)
        
        # Check if user has all required permissions
        return all(perm in user_permissions for perm in self.required_permissions)


class AdminPermission(BasePermission):
    """Permission class for admin-only access."""
    
    def has_permission(self, request, view):
        return (request.user and 
                request.user.is_authenticated and 
                hasattr(request.user, 'profile') and 
                request.user.profile.role == 'admin')


class AnalystPermission(BasePermission):
    """Permission class for analyst and admin access."""
    
    def has_permission(self, request, view):
        return (request.user and 
                request.user.is_authenticated and 
                hasattr(request.user, 'profile') and 
                request.user.profile.role in ['admin', 'analyst'])


class APIUserPermission(BasePermission):
    """Permission class for API users and above."""
    
    def has_permission(self, request, view):
        return (request.user and 
                request.user.is_authenticated and 
                hasattr(request.user, 'profile') and 
                request.user.profile.role in ['admin', 'analyst', 'api_user'])


class RateLimitPermission(BasePermission):
    """
    Permission class that includes rate limiting.
    """
    
    def __init__(self, requests_per_hour: int = 100):
        self.requests_per_hour = requests_per_hour
    
    def has_permission(self, request, view):
        """
        Check rate limiting for authenticated users.
        
        Args:
            request: HTTP request
            view: View being accessed
            
        Returns:
            True if within rate limit, False otherwise
        """
        if not request.user or not request.user.is_authenticated:
            return True  # Let other permission classes handle authentication
        
        # Get user's rate limit based on role
        if hasattr(request.user, 'profile'):
            role_limits = {
                'admin': 1000,
                'analyst': 500,
                'api_user': 200,
                'viewer': 100
            }
            user_limit = role_limits.get(request.user.profile.role, 100)
        else:
            user_limit = 100
        
        # Check rate limiting (simplified implementation)
        # In production, use Redis or database for rate limiting
        return True  # Placeholder - implement actual rate limiting


class AuthenticationMiddleware:
    """
    Custom middleware for enhanced authentication handling.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Process request
        response = self.get_response(request)
        
        # Add authentication headers
        if hasattr(request, 'user') and request.user.is_authenticated:
            response['X-User-Role'] = getattr(request.user.profile, 'role', 'viewer')
            response['X-User-Id'] = str(request.user.id)
        
        return response


class APIKeyAuthentication:
    """
    API key authentication for programmatic access.
    """
    
    @staticmethod
    def authenticate_api_key(api_key: str) -> Optional[User]:
        """
        Authenticate using API key.
        
        Args:
            api_key: API key
            
        Returns:
            User object or None
        """
        try:
            profile = UserProfile.objects.get(api_key=api_key)
            if profile.user.is_active:
                return profile.user
        except UserProfile.DoesNotExist:
            pass
        
        return None
    
    @staticmethod
    def generate_api_key(user: User) -> str:
        """
        Generate API key for user.
        
        Args:
            user: User object
            
        Returns:
            Generated API key
        """
        import secrets
        
        api_key = secrets.token_urlsafe(32)
        
        if hasattr(user, 'profile'):
            user.profile.api_key = api_key
            user.profile.save()
        else:
            UserProfile.objects.create(user=user, api_key=api_key)
        
        return api_key


# Convenience functions
def require_permissions(permissions: List[str]):
    """
    Decorator to require specific permissions.
    
    Args:
        permissions: List of required permissions
        
    Returns:
        Permission class
    """
    return RoleBasedPermission(permissions)


def require_admin():
    """Decorator to require admin permissions."""
    return AdminPermission()


def require_analyst():
    """Decorator to require analyst or admin permissions."""
    return AnalystPermission()


def require_api_user():
    """Decorator to require API user or higher permissions."""
    return APIUserPermission()


# Global authentication system instance
auth_system = AuthenticationSystem()
