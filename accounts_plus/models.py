from django.contrib.auth.models import User
from django.db import models


class UserN8NProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    n8n_user_id = models.CharField(max_length=64)
    api_key = models.CharField(max_length=255)
    onboarding_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} -> {self.n8n_user_id}"
