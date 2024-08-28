from django.db import models
from django.contrib.auth.models import User
import uuid

# Create your models here.

class Application(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

class RedemptionCode(models.Model):
    code = models.CharField(max_length=12, unique=True, editable=False, blank=True)
    application = models.ForeignKey(Application, on_delete=models.CASCADE, null=True, blank=True)
    expiration_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = uuid.uuid4().hex[:12].upper()
        super().save(*args, **kwargs)
