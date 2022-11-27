from .models import User
from django.contrib.auth.backends import ModelBackend

class EmailLogin(ModelBackend):
    def authenticate(self, request, email=None, password=None):
        try: 
            user = User.objects.get(email=email)
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        except User.DoesNotExist:
            return None
        
    def get_user(self, id):
        try:
            return User.objects.get(pk=id)
        except:
            return None