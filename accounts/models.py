from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)  # E-posta adresi benzersiz olacak
    analysis_credits = models.PositiveIntegerField(default=0)
    is_active_member = models.BooleanField(default=False)
