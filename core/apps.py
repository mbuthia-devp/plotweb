from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        from django.contrib.auth.signals import user_logged_in
        from .models import LoginEvent

        def record_login(sender, request, user, **kwargs):
            forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
            ip = forwarded.split(',')[0].strip() if forwarded else request.META.get('REMOTE_ADDR')
            LoginEvent.objects.create(user=user, ip_address=ip or None)

        user_logged_in.connect(record_login)