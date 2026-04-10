from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext as _
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import Project, StatusHistory
from recommendations.models import Notification

@receiver(post_save, sender=StatusHistory)
def notify_on_status_change(sender, instance, created, **kwargs):
    """Notify the project owner when a status change is recorded in history."""
    if created:
        project = instance.project
        user = project.created_by
        
        status_display = dict(Project.Status.choices).get(instance.new_status, instance.new_status)
        
        title = f"Statut mis à jour : {project.title[:30]}..."
        message = f"Votre projet '{project.title}' est maintenant '{status_display}'."
        
        if instance.comment:
            message += f"\nCommentaire : {instance.comment}"
            
        notification = Notification.objects.create(
            user=user,
            title=title,
            message=message,
            type=Notification.Type.INFO if instance.new_status != 'rejected' else Notification.Type.WARNING
        )
        
        # Real-time WebSocket Notification
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"user_{user.id}_notifications",
                {
                    "type": "notification_message",
                    "content": {
                        "id": notification.id,
                        "title": notification.title,
                        "message": notification.message,
                        "type": notification.type,
                        "created_at": notification.created_at.isoformat(),
                    }
                }
            )
        
        # Optional Email Notification
        if user.email_notifications:
            from django.core.mail import send_mail
            from django.conf import settings
            try:
                send_mail(
                    subject=title,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Error sending notification email: {e}")
