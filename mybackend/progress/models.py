from django.db import models
from django.contrib.auth.models import User


class Experience(models.Model):
    TYPE_CHOICES = (
        ("offer", "Offer"),
        ("request", "Request"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    skill = models.CharField(max_length=255)
    reason = models.TextField(blank=True)
    timeline = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Reflection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="progress_reflections")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
