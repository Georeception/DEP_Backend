from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from .models.news import News
from .models.events import Event
from .models.leadership import NationalLeadership
from .services.email_service import EmailService

@receiver(post_save, sender=News)
def send_news_notification(sender, instance, created, **kwargs):
    """
    Send newsletter when new news is posted
    """
    if created:
        subject = f"New News: {instance.title}"
        html_content = render_to_string('newsletter/news_notification.html', {
            'title': instance.title,
            'content': instance.content,
            'date': instance.created_at,
            'url': f"/news/{instance.id}"
        })
        EmailService.send_newsletter(subject, html_content)

@receiver(post_save, sender=Event)
def send_event_notification(sender, instance, created, **kwargs):
    """
    Send newsletter when new event is created
    """
    if created:
        subject = f"New Event: {instance.title}"
        html_content = render_to_string('newsletter/event_notification.html', {
            'title': instance.title,
            'description': instance.description,
            'date': instance.date,
            'location': instance.location,
            'url': f"/events/{instance.id}"
        })
        EmailService.send_newsletter(subject, html_content)

@receiver(post_save, sender=NationalLeadership)
def send_leadership_notification(sender, instance, created, **kwargs):
    """
    Send newsletter when new leadership position is appointed
    """
    if created:
        subject = f"New Leadership Appointment: {instance.position}"
        html_content = render_to_string('newsletter/leadership_notification.html', {
            'position': instance.position,
            'name': instance.name,
            'bio': instance.bio,
            'url': f"/leadership/{instance.id}"
        })
        EmailService.send_newsletter(subject, html_content) 