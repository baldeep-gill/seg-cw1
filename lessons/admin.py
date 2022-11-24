from django.contrib import admin
from .models import Admin

# Register your models here.
@admin.register(Admin)
class UserAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for users."""

    list_display = [
        'username', 'first_name', 'last_name', 'email', 'is_active',
    ]