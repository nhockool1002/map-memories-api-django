from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from django.core.exceptions import PermissionDenied
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that returns consistent error responses
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Log the error
        logger.error(f"API Error: {exc} - Context: {context}")
        
        # Get the status code
        status_code = response.status_code
        
        # Determine error message and type
        if status_code == status.HTTP_400_BAD_REQUEST:
            error_type = "validation_error"
            message = "Validation failed"
        elif status_code == status.HTTP_401_UNAUTHORIZED:
            error_type = "authentication_error"
            message = "Authentication required"
        elif status_code == status.HTTP_403_FORBIDDEN:
            error_type = "permission_error"
            message = "Permission denied"
        elif status_code == status.HTTP_404_NOT_FOUND:
            error_type = "not_found_error"
            message = "Resource not found"
        elif status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
            error_type = "method_error"
            message = "Method not allowed"
        elif status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            error_type = "rate_limit_error"
            message = "Too many requests"
        elif status_code >= 500:
            error_type = "server_error"
            message = "Internal server error"
        else:
            error_type = "error"
            message = "An error occurred"
        
        # Extract error details
        errors = response.data
        if isinstance(errors, dict):
            # Handle field validation errors
            if 'detail' in errors:
                error_message = str(errors['detail'])
            else:
                # Handle field-specific errors
                error_details = {}
                for field, field_errors in errors.items():
                    if isinstance(field_errors, list):
                        error_details[field] = field_errors
                    else:
                        error_details[field] = [str(field_errors)]
                error_message = message
                errors = error_details
        else:
            error_message = str(errors) if errors else message
            errors = None
        
        # Create consistent error response
        custom_response_data = {
            'success': False,
            'message': error_message,
            'error_type': error_type,
            'status_code': status_code
        }
        
        # Add errors if they exist
        if errors:
            custom_response_data['errors'] = errors
        
        response.data = custom_response_data
    
    return response


def handle_404(request, exception):
    """
    Handle 404 errors with consistent JSON response
    """
    return Response({
        'success': False,
        'message': 'Page not found',
        'error_type': 'not_found_error',
        'status_code': 404
    }, status=status.HTTP_404_NOT_FOUND)


def handle_500(request):
    """
    Handle 500 errors with consistent JSON response
    """
    logger.error("Internal server error occurred")
    return Response({
        'success': False,
        'message': 'Internal server error',
        'error_type': 'server_error',
        'status_code': 500
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)