from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Roadmap, Activity, Event, Reflection, Post


# =========================
# USER
# =========================
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


# =========================
# ROADMAP
# =========================
class RoadmapSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Roadmap
        fields = ["id", "user_id", "skill", "start_date", "end_date", "steps", "completed", "created_at"]
        read_only_fields = ["id", "created_at"]

    def create(self, validated_data):
        user_id = validated_data.pop("user_id")
        return Roadmap.objects.create(user_id=user_id, **validated_data)


# =========================
# ACTIVITY
# =========================
class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = "__all__"


# =========================
# EVENTS (CALENDAR)
# =========================
class EventSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Event
        fields = ["id", "user_id", "title", "type", "date", "completed"]

    def create(self, validated_data):
        user_id = validated_data.pop("user_id")
        return Event.objects.create(user_id=user_id, **validated_data)


# =========================
# WEEKLY REFLECTION
# =========================
from .models import Reflection

class ReflectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reflection
        fields = "__all__"

# serializers.py
class PostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.username", read_only=True)
    author_headline = serializers.CharField(source="author.profile.headline", read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "text",
            "skill",
            "created_at",
            "author",
            "author_name",        # 🔥 ADD THIS
            "author_headline",    # 🔥 ADD THIS
            "image",
            "likes_count",
            "comments_count",
        ]
