from djangocas.backends import CASBackend
from django.contrib.auth import get_user_model


class ITSBackend(CASBackend):   

    #Override
    def get_or_init_user(self, username):
        User = get_user_model()
        try:
            user = User.objects.get(username=username, is_active=True)
        except User.DoesNotExist:
            return None
                
        return user