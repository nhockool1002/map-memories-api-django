import os
import uuid
import base64
import mimetypes
from PIL import Image
from django.core.files.base import ContentFile
from django.conf import settings
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


def generate_unique_filename(original_filename: str) -> str:
    """
    Generate a unique filename while preserving the original extension
    """
    name, ext = os.path.splitext(original_filename)
    unique_name = f"{uuid.uuid4().hex}{ext}"
    return unique_name


def validate_file_size(file_size: int, max_size: int = None) -> bool:
    """
    Validate file size against maximum allowed size
    """
    if max_size is None:
        max_size = settings.MAP_MEMORIES_SETTINGS['MAX_FILE_SIZE']
    
    return file_size <= max_size


def validate_file_type(content_type: str) -> Tuple[bool, str]:
    """
    Validate file type and return whether it's valid and what type it is
    Returns: (is_valid, media_type)
    """
    allowed_images = settings.MAP_MEMORIES_SETTINGS['ALLOWED_IMAGE_TYPES']
    allowed_videos = settings.MAP_MEMORIES_SETTINGS['ALLOWED_VIDEO_TYPES']
    
    if content_type in allowed_images:
        return True, 'image'
    elif content_type in allowed_videos:
        return True, 'video'
    else:
        return False, None


def encode_file_to_base64(file_content: bytes, content_type: str) -> str:
    """
    Encode file content to base64 data URL
    """
    base64_encoded = base64.b64encode(file_content).decode('utf-8')
    return f"data:{content_type};base64,{base64_encoded}"


def decode_base64_file(base64_string: str) -> Tuple[bytes, str]:
    """
    Decode base64 data URL to file content and content type
    Returns: (file_content, content_type)
    """
    try:
        # Parse data URL format: data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...
        header, encoded = base64_string.split(',', 1)
        content_type = header.split(':')[1].split(';')[0]
        file_content = base64.b64decode(encoded)
        return file_content, content_type
    except Exception as e:
        logger.error(f"Error decoding base64 file: {e}")
        raise ValueError("Invalid base64 file data")


def process_image_upload(file) -> dict:
    """
    Process image upload and return file information
    """
    try:
        # Validate file size
        if not validate_file_size(file.size):
            raise ValueError(f"File size too large. Maximum size is {settings.MAP_MEMORIES_SETTINGS['MAX_FILE_SIZE']} bytes")
        
        # Validate file type
        content_type = file.content_type
        is_valid, media_type = validate_file_type(content_type)
        
        if not is_valid:
            raise ValueError(f"File type not supported: {content_type}")
        
        # Generate unique filename
        filename = generate_unique_filename(file.name)
        
        # Read file content
        file_content = file.read()
        
        # Encode to base64
        base64_data = encode_file_to_base64(file_content, content_type)
        
        return {
            'filename': filename,
            'original_filename': file.name,
            'file_size': file.size,
            'content_type': content_type,
            'media_type': media_type,
            'base64_data': base64_data
        }
    
    except Exception as e:
        logger.error(f"Error processing file upload: {e}")
        raise


def get_image_dimensions(file_content: bytes) -> Tuple[int, int]:
    """
    Get image dimensions from file content
    Returns: (width, height)
    """
    try:
        with Image.open(ContentFile(file_content)) as img:
            return img.size
    except Exception as e:
        logger.error(f"Error getting image dimensions: {e}")
        return (0, 0)


def create_image_thumbnail(file_content: bytes, size: Tuple[int, int] = (300, 300)) -> bytes:
    """
    Create thumbnail from image content
    """
    try:
        with Image.open(ContentFile(file_content)) as img:
            # Convert to RGB if necessary (for PNG with transparency)
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Create thumbnail
            img.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Save to bytes
            from io import BytesIO
            output = BytesIO()
            img.save(output, format='JPEG', quality=85)
            return output.getvalue()
    
    except Exception as e:
        logger.error(f"Error creating thumbnail: {e}")
        return file_content  # Return original if thumbnail creation fails


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing or replacing invalid characters
    """
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Limit length
    name, ext = os.path.splitext(filename)
    if len(name) > 50:
        name = name[:50]
    
    return f"{name}{ext}"


def get_file_extension(filename: str) -> str:
    """
    Get file extension from filename
    """
    return os.path.splitext(filename)[1].lower()


def guess_content_type(filename: str) -> str:
    """
    Guess content type from filename
    """
    content_type, _ = mimetypes.guess_type(filename)
    return content_type or 'application/octet-stream'


class FileProcessor:
    """
    Class for processing various file operations
    """
    
    @staticmethod
    def process_media_file(uploaded_file):
        """
        Process uploaded media file and return processed data
        """
        return process_image_upload(uploaded_file)
    
    @staticmethod
    def validate_media_file(uploaded_file) -> bool:
        """
        Validate uploaded media file
        """
        try:
            # Check file size
            if not validate_file_size(uploaded_file.size):
                return False
            
            # Check file type
            is_valid, _ = validate_file_type(uploaded_file.content_type)
            return is_valid
        
        except Exception:
            return False
    
    @staticmethod
    def get_media_info(uploaded_file) -> dict:
        """
        Get media file information
        """
        info = {
            'name': uploaded_file.name,
            'size': uploaded_file.size,
            'content_type': uploaded_file.content_type,
        }
        
        # Add media type
        is_valid, media_type = validate_file_type(uploaded_file.content_type)
        info['media_type'] = media_type if is_valid else None
        
        # Add dimensions for images
        if media_type == 'image':
            try:
                file_content = uploaded_file.read()
                uploaded_file.seek(0)  # Reset file pointer
                width, height = get_image_dimensions(file_content)
                info['width'] = width
                info['height'] = height
            except Exception:
                info['width'] = 0
                info['height'] = 0
        
        return info