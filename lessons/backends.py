from .models import User
from django.contrib.auth.backends import ModelBackend

class EmailLogin(ModelBackend):
    '''referenced django docs https://docs.djangoproject.com/en/4.1/topics/auth/customizing/'''
    # custom authentication using email instead of username which django specifies by default
    def authenticate(self, request, username=None, password=None):
        try: 
            user = User.objects.get(email=username)
            # checks password and if the user is active
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        except User.DoesNotExist:
            return None
        
    def get_user(self, id):
        try:
            return User.objects.get(pk=id)
        except:
            return None