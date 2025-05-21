from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings
import requests
import json
import base64
import logging

logger = logging.getLogger(__name__)

class BrevoEmailBackend(BaseEmailBackend):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_key = settings.BREVO_API_KEY
        self.api_url = 'https://api.brevo.com/v3/smtp/email'

    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        success_count = 0
        for message in email_messages:
            try:
                # Handle attachments if present
                attachments = []
                if hasattr(message, 'attachments'):
                    for attachment in message.attachments:
                        if isinstance(attachment, tuple):
                            filename, content, mimetype = attachment
                            attachments.append({
                                'name': filename,
                                'content': base64.b64encode(content).decode('utf-8'),
                                'contentType': mimetype
                            })

                payload = {
                    'sender': {
                        'email': settings.DEFAULT_FROM_EMAIL,
                        'name': 'Devolution Empowerment Party'
                    },
                    'to': [{'email': recipient} for recipient in message.to],
                    'subject': message.subject,
                    'htmlContent': message.body if message.content_subtype == 'html' else None,
                    'textContent': message.body if message.content_subtype == 'plain' else None,
                    'attachment': attachments if attachments else None
                }

                headers = {
                    'accept': 'application/json',
                    'content-type': 'application/json',
                    'api-key': self.api_key
                }

                response = requests.post(
                    self.api_url,
                    headers=headers,
                    data=json.dumps(payload)
                )
                
                if response.status_code == 201:
                    success_count += 1
                    logger.info(f"Email sent successfully to {message.to}")
                else:
                    logger.error(f"Failed to send email: {response.text}")
                    print(f"Failed to send email: {response.text}")
                    
            except Exception as e:
                logger.error(f"Error sending email: {str(e)}", exc_info=True)
                print(f"Error sending email: {str(e)}")
                continue

        return success_count 