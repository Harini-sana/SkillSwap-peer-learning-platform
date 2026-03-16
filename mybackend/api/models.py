from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


# =======================
# Newsletter
# =======================
class Newsletter(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


# =======================
# Contact Messages
# =======================
class ContactMessage(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"

# =======================
# Skills (Offer / Request)
# =======================
class Skill(models.Model):
    OFFER = 'offer'
    REQUEST = 'request'
    TYPE_CHOICES = [
        (OFFER, 'Offer'),
        (REQUEST, 'Request'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    reason = models.TextField(blank=True)
    timeline = models.CharField(max_length=50, blank=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)


# =======================
# Skill Experience (Progress)
# =======================
class SkillExperience(models.Model):
    TYPE_CHOICES = (
        ('learn', 'Learn'),
        ('teach', 'Teach'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='skill_experiences')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    skill = models.CharField(max_length=100)
    person = models.CharField(max_length=100, blank=True)
    date = models.DateField()
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.skill} ({self.type})"


# =======================
# Roadmaps
# =======================
class Roadmap(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="roadmaps")
    skill = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    steps = models.JSONField()
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.skill} ({self.user.username})"


# =======================
# Activity Feed
# =======================
class Activity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="activities")
    text = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.text}"


# =======================
# Calendar Events
# =======================
class Event(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="events")
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=50)
    date = models.DateField()
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    exchange_id = models.IntegerField(null=True, blank=True) 

# =======================
# Weekly Reflections (ONLY ONE Reflection MODEL)
# =======================
class Reflection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="weekly_reflections")
    text = models.TextField()
    week = models.CharField(max_length=20, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.week}"

# explore page - till  like
from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    skill = models.CharField(max_length=100)
    image = models.ImageField(upload_to="posts/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class SavedPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

#CONNECT PAGE 
#user profile
from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_views = models.IntegerField(default=0)
    subtitle = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True)
    skills = models.JSONField(default=list)   # ["Python", "UI Design"]
    verified = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)
    rating = models.FloatField(default=4.5)

    def __str__(self):
        return self.user.username

#exchange request

from django.db import models
from django.contrib.auth.models import User

class ExchangeRequest(models.Model):
    from_user = models.ForeignKey(User, related_name="sent_requests", on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name="received_requests", on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default="pending")  # pending, accepted, rejected
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.from_user} → {self.to_user} ({self.status})"

#EXCHANGE ROOM
from django.db import models
from django.contrib.auth.models import User

class Exchange(models.Model):
    user_a = models.ForeignKey(User, related_name="exchange_a", on_delete=models.CASCADE)
    user_b = models.ForeignKey(User, related_name="exchange_b", on_delete=models.CASCADE)
    skill_a = models.CharField(max_length=100)
    skill_b = models.CharField(max_length=100)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, default="pending")  # pending / completed

    created_at = models.DateTimeField(auto_now_add=True)


class ExchangeMessage(models.Model):
    exchange = models.ForeignKey(Exchange, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


#MESSAGE PAGE

# api/models.py
# =======================
# Chat Messages (ONLY ONE MESSAGE MODEL)
# =======================
class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")

    content = models.TextField(blank=True)

    post = models.ForeignKey("Post", on_delete=models.SET_NULL, null=True, blank=True)

    # 🔥 ADD THIS
    request_from = models.IntegerField(null=True, blank=True)

    timestamp = models.DateTimeField(auto_now_add=True)
    seen = models.BooleanField(default=False)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return f"{self.sender} → {self.receiver}: {self.content[:20]}"

class Report(models.Model):
    reported_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reports_against")
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reports_made")
    report_type = models.CharField(max_length=100)
    report_location = models.CharField(max_length=100)
    description = models.TextField()
    evidence = models.FileField(upload_to="reports/", null=True, blank=True)
    status = models.CharField(max_length=50, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

from django.db import models
from django.contrib.auth.models import User

class Certificate(models.Model):
    CERT_TYPE_CHOICES = [
        ("self-study", "Self Study"),
        ("exchange", "Skill Exchange"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    certificate_id = models.CharField(max_length=50, unique=True)
    type = models.CharField(max_length=20, choices=CERT_TYPE_CHOICES)
    skill = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.type} - {self.certificate_id}"

# api/models.py
class ExchangeRating(models.Model):
    exchange = models.ForeignKey("Exchange", on_delete=models.CASCADE)
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="given_ratings")
    reviewed_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_ratings")
    rating = models.IntegerField()
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reviewer} → {self.reviewed_user} ({self.rating})"