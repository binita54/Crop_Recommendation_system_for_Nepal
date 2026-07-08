from .models import Notification, UserProfile

def unread_notifications(request):
    count = 0
    if request.user.is_authenticated:
        count = request.user.notifications.filter(is_read=False).count()
    return {'unread_notifications_count': count}


def language_context(request):
    preferred_language = 'en'
    if request.user.is_authenticated:
        try:
            profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.filter(user=request.user).first()
        if profile and profile.preferred_language:
            preferred_language = profile.preferred_language
    return {'preferred_language': preferred_language}