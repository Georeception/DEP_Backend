# Backend Cloudinary Integration Guide

This document explains how Cloudinary is integrated into our Django backend for handling media uploads.

## Overview

We use Cloudinary for storing and serving media files (images and videos) in our application. The integration is handled through the `django-cloudinary-storage` package, which provides a seamless way to store and serve media files through Cloudinary's CDN.

## Setup

1. Install required packages:
```bash
pip install django-cloudinary-storage
```

2. Add to `INSTALLED_APPS` in `settings.py`:
```python
INSTALLED_APPS = [
    ...
    'cloudinary_storage',
    'django.contrib.staticfiles',
    ...
]
```

3. Configure Cloudinary settings in `settings.py`:
```python
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'your_cloud_name',
    'API_KEY': 'your_api_key',
    'API_SECRET': 'your_api_secret'
}

# Set default file storage to Cloudinary
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
```

## Model Implementation

### 1. Image Fields

All image fields in our models use `MediaCloudinaryStorage` for automatic upload to Cloudinary:

```python
from cloudinary_storage.storage import MediaCloudinaryStorage

class YourModel(models.Model):
    image = models.ImageField(
        upload_to='your_folder/',  # Cloudinary folder path
        storage=MediaCloudinaryStorage()
    )
```

### 2. URL Handling

Each model with image fields includes a method to get the Cloudinary URL:

```python
def get_image_url(self):
    if not self.image:
        return None
    if str(self.image).startswith('v'):
        return f"https://res.cloudinary.com/{settings.CLOUDINARY_STORAGE['CLOUD_NAME']}/image/upload/{self.image}"
    return self.image.url if self.image else None
```

## Models Using Cloudinary

### 1. News Model
- `preview_image`: Uploads to 'news/previews/'
- `image`: Uploads to 'news/'

### 2. Gallery Model
- `image`: Uploads to 'gallery/images/'
- `video`: Uploads to 'gallery/videos/'
- `thumbnail`: Uploads to 'gallery/thumbnails/'

### 3. Events Model
- `preview_image`: Uploads to 'events/previews/'

### 4. Product Model
- `image`: Uploads to 'products/'

## Usage

1. **Uploading Images**
   - Images are automatically uploaded to Cloudinary when saved through Django's admin interface or API
   - No additional code needed - the storage backend handles everything

2. **Accessing Images**
   - Use the model's `get_image_url()` method to get the Cloudinary URL
   - Example: `news_item.get_preview_image_url()`

3. **Image Transformations**
   - Cloudinary URLs can be modified to include transformations
   - Example: Add `/w_300,h_200,c_fill` to resize and crop

## Cloudinary Limitations

### Free Tier Limits
1. **Video Uploads**
   - Maximum file size: 10MB
   - Maximum duration: 10 seconds
   - Maximum resolution: 720p
   - Note: These limits are set by Cloudinary's free tier and cannot be modified without upgrading to a paid plan

2. **Image Uploads**
   - No strict file size limits
   - Recommended to keep images under 10MB for optimal performance

### Handling Large Files
If you need to handle larger video files, consider:
1. Upgrading to a paid Cloudinary plan
2. Implementing a different video storage solution
3. Using video compression before upload
4. Implementing chunked uploads for larger files

## Best Practices

1. **Folder Structure**
   - Keep a consistent folder structure in Cloudinary
   - Use descriptive folder names
   - Separate different types of media (images, videos, thumbnails)

2. **Error Handling**
   - Always check if image exists before accessing URL
   - Handle cases where image might be null
   - Implement file size validation before upload
   - Add appropriate error messages for file size limits

3. **Performance**
   - Use appropriate image sizes
   - Consider using Cloudinary's automatic format optimization
   - Use lazy loading for images in frontend
   - Compress videos before upload when possible

## Troubleshooting

1. **Image Not Uploading**
   - Check Cloudinary credentials
   - Verify storage backend is properly configured
   - Check file permissions

2. **URL Not Working**
   - Verify the image exists in Cloudinary
   - Check if the URL is properly formatted
   - Ensure Cloudinary settings are correct

3. **Video Upload Issues**
   - Check if file size exceeds 10MB limit
   - Verify video duration is under 10 seconds
   - Ensure video resolution is 720p or lower
   - Check if video format is supported by Cloudinary

## Security

1. **API Keys**
   - Never commit API keys to version control
   - Use environment variables for sensitive data
   - Regularly rotate API keys

2. **Upload Restrictions**
   - Set appropriate upload limits
   - Validate file types
   - Implement user authentication for uploads
   - Add file size validation in forms and API endpoints

## Additional Resources

- [Cloudinary Documentation](https://cloudinary.com/documentation)
- [Django Cloudinary Storage Documentation](https://django-cloudinary-storage.readthedocs.io/)
- [Cloudinary Image Transformations](https://cloudinary.com/documentation/image_transformations)
- [Cloudinary Video Upload Limits](https://cloudinary.com/documentation/video_upload) 