from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from ..models.newsletter import NewsletterSubscription
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)

class EmailService:
    @staticmethod
    def send_newsletter(subject, html_content, context=None):
        """
        Send newsletter to all active subscribers
        """
        subscribers = NewsletterSubscription.objects.filter(status='active', is_verified=True)
        
        for subscriber in subscribers:
            # Render the email template with context
            html_message = render_to_string(html_content, context) if context else html_content
            plain_message = strip_tags(html_message)
            
            try:
                send_mail(
                    subject=subject,
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[subscriber.email],
                    html_message=html_message,
                    fail_silently=False,
                )
            except Exception as e:
                logger.error(f"Failed to send email to {subscriber.email}: {str(e)}")
                print(f"Failed to send email to {subscriber.email}: {str(e)}")

    @staticmethod
    def send_verification_email(subscriber):
        """
        Send verification email to new subscribers
        """
        try:
            verification_token = subscriber.generate_verification_token()
            verification_url = f"{settings.FRONTEND_URL}/verify-newsletter/{verification_token}"
            current_year = datetime.now().year
            
            subject = "Verify your newsletter subscription"
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style type="text/css">
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        margin: 0;
                        padding: 0;
                        background-color: #f4f4f4;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 0;
                        background-color: #ffffff;
                        border-radius: 8px;
                        overflow: hidden;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }}
                    .header {{
                        background-color: #1a237e;
                        padding: 30px 20px;
                        text-align: center;
                        color: white;
                    }}
                    .header h1 {{
                        margin: 0;
                        font-size: 24px;
                        font-weight: 600;
                    }}
                    .content {{
                        padding: 40px 20px;
                        text-align: center;
                    }}
                    .welcome-text {{
                        font-size: 18px;
                        color: #1a237e;
                        margin-bottom: 30px;
                    }}
                    .button {{
                        display: inline-block;
                        padding: 15px 30px;
                        background-color: #4CAF50;
                        color: white;
                        text-decoration: none;
                        border-radius: 25px;
                        font-size: 16px;
                        font-weight: 600;
                        margin: 20px 0;
                        transition: background-color 0.3s ease;
                    }}
                    .button:hover {{
                        background-color: #45a049;
                    }}
                    .footer {{
                        background-color: #f8f9fa;
                        padding: 20px;
                        text-align: center;
                        font-size: 12px;
                        color: #666;
                        border-top: 1px solid #eee;
                    }}
                    .social-links {{
                        margin: 20px 0;
                    }}
                    .social-links a {{
                        color: #1a237e;
                        text-decoration: none;
                        margin: 0 10px;
                    }}
                    @media only screen and (max-width: 600px) {{
                        .container {{
                            width: 100% !important;
                            border-radius: 0;
                        }}
                        .content {{
                            padding: 20px;
                        }}
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Devolution Empowerment Party</h1>
                    </div>
                    <div class="content">
                        <div class="welcome-text">
                            <h2>Welcome to Our Newsletter!</h2>
                            <p>Thank you for joining our community. We're excited to have you on board!</p>
                        </div>
                        <p>To ensure you receive our updates, please verify your email address by clicking the button below:</p>
                        <a href="{verification_url}" class="button">Verify Email Address</a>
                        <div class="social-links">
                            <p>Follow us on social media:</p>
                            <a href="#">Facebook</a> |
                            <a href="#">Twitter</a> |
                            <a href="#">Instagram</a>
                        </div>
                    </div>
                    <div class="footer">
                        <p>If you did not request this subscription, please ignore this email.</p>
                        <p>© {current_year} Devolution Empowerment Party. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Create email message
            email = EmailMessage(
                subject=subject,
                body=html_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[subscriber.email],
                headers={'Content-Type': 'text/html'}
            )

            # Send the email
            email.send()
            logger.info(f"Verification email sent successfully to {subscriber.email}")
            
        except Exception as e:
            logger.error(f"Failed to send verification email to {subscriber.email}: {str(e)}", exc_info=True)
            print(f"Failed to send verification email to {subscriber.email}: {str(e)}")
            raise  # Re-raise the exception to handle it in the view 