from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import User, UserSession


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Custom admin interface for User model
    """
    list_display = (
        'username', 'email', 'full_name', 'is_admin', 
        'currency', 'is_active', 'created_at', 'deleted_status'
    )
    list_filter = (
        'is_admin', 'is_active', 'is_staff', 'is_superuser',
        'created_at', 'deleted_at'
    )
    search_fields = ('username', 'email', 'full_name')
    ordering = ('-created_at',)
    readonly_fields = ('uuid', 'created_at', 'updated_at', 'deleted_at')
    
    # Custom fieldsets for the admin form
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Personal info', {
            'fields': ('email', 'full_name', 'avatar_url')
        }),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser', 'is_admin',
                'groups', 'user_permissions'
            ),
        }),
        ('Currency & Gaming', {
            'fields': ('currency',),
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at', 'deleted_at')
        }),
        ('System', {
            'fields': ('uuid',),
            'classes': ('collapse',)
        }),
    )
    
    # Fieldsets for adding a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
        ('Personal info', {
            'fields': ('full_name',)
        }),
        ('Permissions', {
            'fields': ('is_admin',)
        }),
        ('Currency', {
            'fields': ('currency',)
        }),
    )
    
    def deleted_status(self, obj):
        """Display deletion status with color coding"""
        if obj.deleted_at:
            return format_html(
                '<span style="color: red;">Deleted</span>'
            )
        return format_html(
            '<span style="color: green;">Active</span>'
        )
    deleted_status.short_description = 'Status'
    
    def get_queryset(self, request):
        """Include soft-deleted users in admin"""
        return User.all_objects.all()
    
    actions = ['restore_users', 'soft_delete_users', 'add_currency', 'subtract_currency']
    
    def restore_users(self, request, queryset):
        """Restore soft-deleted users"""
        restored_count = 0
        for user in queryset:
            if user.is_deleted:
                user.restore()
                restored_count += 1
        
        self.message_user(
            request,
            f'Successfully restored {restored_count} user(s).'
        )
    restore_users.short_description = "Restore selected users"
    
    def soft_delete_users(self, request, queryset):
        """Soft delete users"""
        deleted_count = 0
        for user in queryset:
            if not user.is_deleted:
                user.delete()
                deleted_count += 1
        
        self.message_user(
            request,
            f'Successfully deleted {deleted_count} user(s).'
        )
    soft_delete_users.short_description = "Soft delete selected users"
    
    def add_currency(self, request, queryset):
        """Add 1000 currency to selected users"""
        for user in queryset:
            if not user.is_deleted:
                user.add_currency(1000, "Admin bonus from admin panel")
        
        self.message_user(
            request,
            f'Added 1000 currency to {queryset.count()} user(s).'
        )
    add_currency.short_description = "Add 1000 currency to selected users"
    
    def subtract_currency(self, request, queryset):
        """Subtract 500 currency from selected users"""
        for user in queryset:
            if not user.is_deleted and user.currency >= 500:
                user.subtract_currency(500, "Admin deduction from admin panel")
        
        self.message_user(
            request,
            f'Subtracted 500 currency from selected users.'
        )
    subtract_currency.short_description = "Subtract 500 currency from selected users"


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    """
    Admin interface for UserSession model
    """
    list_display = ('user', 'token_preview', 'expires_at', 'is_expired_status', 'created_at')
    list_filter = ('expires_at', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('token_hash', 'created_at')
    ordering = ('-created_at',)
    
    def token_preview(self, obj):
        """Show first and last 8 characters of token hash"""
        if len(obj.token_hash) > 16:
            return f"{obj.token_hash[:8]}...{obj.token_hash[-8:]}"
        return obj.token_hash
    token_preview.short_description = 'Token (preview)'
    
    def is_expired_status(self, obj):
        """Display expiration status with color coding"""
        if obj.is_expired():
            return format_html(
                '<span style="color: red;">Expired</span>'
            )
        return format_html(
            '<span style="color: green;">Active</span>'
        )
    is_expired_status.short_description = 'Status'
    
    actions = ['delete_expired_sessions']
    
    def delete_expired_sessions(self, request, queryset):
        """Delete expired sessions"""
        expired_sessions = [session for session in queryset if session.is_expired()]
        count = len(expired_sessions)
        
        for session in expired_sessions:
            session.delete()
        
        self.message_user(
            request,
            f'Successfully deleted {count} expired session(s).'
        )