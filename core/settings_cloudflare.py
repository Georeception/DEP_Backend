"""
Django settings for Cloudflare Workers deployment.

This module extends the base settings.py with Cloudflare-specific configurations:
- Hyperdrive database connection pooling
- Serverless-optimized caching
- Cloud storage for media files (Workers are read-only)
- Serverless-optimized performance settings

Environment variable RUNNING_ON_CLOUDFLARE is set by wrangler.toml
"""

from .settings import *  # Import all settings from base settings.py
import os
import dj_database_url

# Detect if running on Cloudflare Workers
RUNNING_ON_CLOUDFLARE = os.getenv('RUNNING_ON_CLOUDFLARE', 'false').lower() in {'true', '1', 'yes'}

if RUNNING_ON_CLOUDFLARE:
    # ============================================================================
    # CLOUDFLARE WORKERS - DATABASE CONFIGURATION (HYPERDRIVE)
    # ============================================================================

    # Hyperdrive injects database connection via binding or environment variable
    # Priority: DB binding > DB_CONNECTION_STRING > DATABASE_URL > fallback
    hyperdrive_binding = os.getenv('DB')  # Cloudflare Hyperdrive binding
    db_connection_string = os.getenv('DB_CONNECTION_STRING')  # Alternative env var
    database_url = os.getenv('DATABASE_URL')  # Standard DATABASE_URL

    if hyperdrive_binding:
        # Use Hyperdrive binding (preferred for Cloudflare Workers)
        # Hyperdrive manages connection pooling globally, so we set conn_max_age=None
        DATABASES = {
            'default': dj_database_url.config(
                default=hyperdrive_binding,
                conn_max_age=None,  # Hyperdrive manages pooling
                conn_health_checks=True,
                ssl_require=True,
            )
        }
    elif db_connection_string:
        # Use DB_CONNECTION_STRING environment variable
        DATABASES = {
            'default': dj_database_url.config(
                default=db_connection_string,
                conn_max_age=None,  # Hyperdrive manages pooling
                conn_health_checks=True,
                ssl_require=True,
            )
        }
    elif database_url:
        # Fallback to standard DATABASE_URL
        DATABASES = {
            'default': dj_database_url.config(
                default=database_url,
                conn_max_age=None,  # Hyperdrive manages pooling
                conn_health_checks=True,
                ssl_require=True,
            )
        }
    else:
        # Fallback to individual DB credentials (for local testing with wrangler dev)
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': os.getenv('DB_NAME'),
                'USER': os.getenv('DB_USER'),
                'PASSWORD': os.getenv('DB_PASSWORD'),
                'HOST': os.getenv('DB_HOST'),
                'PORT': os.getenv('DB_PORT'),
            }
        }

    # ============================================================================
    # CLOUDFLARE WORKERS - CACHING CONFIGURATION
    # ============================================================================

    # Cloudflare Workers has built-in edge caching via Cache API
    # For session and application-level caching, we use local memory cache
    # Workers are stateless but can use Cloudflare KV or Durable Objects for persistence
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'KEY_PREFIX': 'dep_party_cf',
            'TIMEOUT': 300,  # 5 minutes
        }
    }

    # ============================================================================
    # CLOUDFLARE WORKERS - MEDIA/FILE STORAGE CONFIGURATION
    # ============================================================================

    # Cloudflare Workers has a read-only filesystem
    # All media files must be stored externally (Cloudflare R2, AWS S3, etc.)
    # This is a stub for django-storages configuration

    # Example configuration for Cloudflare R2 (using django-storages and boto3)
    # Uncomment and configure these settings if using R2:
    #
    # STORAGES = {
    #     'default': {
    #         'BACKEND': 'storages.backends.s3boto3.S3Boto3Storage',
    #     },
    #     'staticfiles': {
    #         'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    #     },
    # }
    #
    # AWS_ACCESS_KEY_ID = os.getenv('R2_ACCESS_KEY_ID')
    # AWS_SECRET_ACCESS_KEY = os.getenv('R2_SECRET_ACCESS_KEY')
    # AWS_STORAGE_BUCKET_NAME = os.getenv('R2_BUCKET_NAME')
    # AWS_S3_ENDPOINT_URL = os.getenv('R2_ENDPOINT_URL')  # e.g., https://<account>.r2.cloudflarestorage.com
    # AWS_S3_REGION_NAME = 'auto'
    # AWS_S3_CUSTOM_DOMAIN = os.getenv('R2_CUSTOM_DOMAIN')  # Optional: custom domain for R2
    # AWS_DEFAULT_ACL = None
    # AWS_S3_OBJECT_PARAMETERS = {
    #     'CacheControl': 'max-age=86400',
    # }
    #
    # # Media URL
    # MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/" if AWS_S3_CUSTOM_DOMAIN else f"{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}/"
    #
    # # Override DEFAULT_FILE_STORAGE
    # DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

    # For now, keep using Cloudinary (already configured in base settings)
    # Cloudinary works well with Cloudflare Workers as it's an external storage service
    # No changes needed for Cloudinary configuration

    # ============================================================================
    # CLOUDFLARE WORKERS - STATIC FILES CONFIGURATION
    # ============================================================================

    # Static files should be served via Cloudflare CDN
    # In production, collectstatic and upload to R2 or use Cloudflare Pages
    # For Workers, we can use Cloudflare Assets or R2 for static files

    # Keep WhiteNoise for now (it works with Workers for simple deployments)
    # For production, consider uploading static files to R2 and serving via CDN
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

    # ============================================================================
    # CLOUDFLARE WORKERS - SECURITY CONFIGURATION
    # ============================================================================

    # Cloudflare Workers handles SSL termination at the edge
    # Trust Cloudflare's headers
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    # These are already set in base settings when DEBUG=False, but we ensure them here
    if not DEBUG:
        SECURE_SSL_REDIRECT = True
        SESSION_COOKIE_SECURE = True
        CSRF_COOKIE_SECURE = True
        SECURE_BROWSER_XSS_FILTER = True
        SECURE_CONTENT_TYPE_NOSNIFF = True
        SECURE_HSTS_SECONDS = 31536000
        SECURE_HSTS_INCLUDE_SUBDOMAINS = True
        SECURE_HSTS_PRELOAD = True

    # ============================================================================
    # CLOUDFLARE WORKERS - PERFORMANCE OPTIMIZATIONS
    # ============================================================================

    # Disable Django's autocommit for better performance in serverless environment
    # (PostgreSQL with Hyperdrive handles this efficiently)
    # DATABASES['default']['OPTIONS'] = {
    #     'autocommit': False,
    # }

    # Optimize for serverless cold starts
    # Preload app to reduce initialization time
    # This is already handled by wrangler.toml compatibility flags

    # ============================================================================
    # CLOUDFLARE WORKERS - LOGGING CONFIGURATION
    # ============================================================================

    # Use Cloudflare Workers' built-in logging
    # Logs appear in Cloudflare dashboard
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '{levelname} {asctime} {module} {message}',
                'style': '{',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'verbose',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['console'],
                'level': 'INFO',
                'propagate': True,
            },
            'party': {
                'handlers': ['console'],
                'level': 'INFO',
                'propagate': True,
            },
        },
    }

    # ============================================================================
    # CLOUDFLARE WORKERS - ALLOWED HOSTS
    # ============================================================================

    # Add Cloudflare Workers domain to allowed hosts
    # This can be set via environment variable or configured per deployment
    cloudflare_domain = os.getenv('CLOUDFLARE_WORKERS_DOMAIN')
    if cloudflare_domain and cloudflare_domain not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(cloudflare_domain)

    # Ensure Cloudflare's default preview domain is allowed
    if '*.workers.dev' not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append('*.workers.dev')

else:
    # Not running on Cloudflare - use base settings as-is
    # This ensures settings_cloudflare.py can be used for local testing
    # without Cloudflare environment
    pass
