# writing/utils.py
from .models import WritingPracticeSession

def get_last_session(user):
    return WritingPracticeSession.objects.filter(user=user).order_by("-start_time").first()
