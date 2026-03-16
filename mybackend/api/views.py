from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login as django_login
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
import json
from django.http import JsonResponse
from .models import Certificate
from .models import Newsletter, ContactMessage, Message, Skill
from .models import Exchange, ExchangeMessage, ExchangeRating
from .models import UserProfile


# ======================================================
# AUTH
# ======================================================

@csrf_exempt
def signup(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return JsonResponse({"error": "All fields are required"}, status=400)

    if User.objects.filter(username=username).exists():
        return JsonResponse({"error": "Username already exists"}, status=400)

    if User.objects.filter(email=email).exists():
        return JsonResponse({"error": "Email already exists"}, status=400)

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )

    # 🔑 auto-login after signup
    django_login(request, user)

    return JsonResponse({
        "success": True,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    })
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.models import User
import json
from django.contrib.auth import authenticate, login as django_login
from django.contrib.auth import login as django_login

@csrf_exempt
def login(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    email = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()

    if not email or not password:
        return JsonResponse({"error": "Email and password required"}, status=400)

    try:
        user = User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        return JsonResponse({"error": "Invalid credentials"}, status=400)

    if not user.check_password(password):
        return JsonResponse({"error": "Invalid credentials"}, status=400)

    # 🔥 THIS IS THE FIX
    django_login(request, user)

    return JsonResponse({
        "success": True,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    }, status=200)


@csrf_exempt
def reset_password(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    email = data.get("email")
    if not email:
        return JsonResponse({"error": "Email required"}, status=400)

    if not User.objects.filter(email=email).exists():
        return JsonResponse({"error": "Email not found"}, status=404)

    return JsonResponse({
        "success": True,
        "message": "Password reset link sent!"
    })


# ======================================================
# NEWSLETTER
# ======================================================

@csrf_exempt
def subscribe_newsletter(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    email = data.get("email")
    if not email:
        return JsonResponse({"error": "Email required"}, status=400)

    try:
        Newsletter.objects.create(email=email)
        return JsonResponse({"success": True})
    except IntegrityError:
        return JsonResponse({"error": "Already subscribed"}, status=400)


# ======================================================
# CONTACT
# ======================================================

@csrf_exempt
def submit_contact(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    if not all(data.get(f) for f in ["name", "email", "subject", "message"]):
        return JsonResponse({"error": "All fields required"}, status=400)

    ContactMessage.objects.create(
        name=data["name"],
        email=data["email"],
        subject=data["subject"],
        message=data["message"]
    )

    return JsonResponse({"success": True})

# ======================================================
# SKILLS (FIXED & WORKING)
# ======================================================
@csrf_exempt
def add_skill(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    user_id = data.get("user_id")
    name = data.get("name")
    skill_type = data.get("type")  # "offer" or "request"

    if not user_id or not name or skill_type not in ["offer", "request"]:
        return JsonResponse({"error": "Invalid data"}, status=400)

    user = get_object_or_404(User, id=user_id)

    skill = Skill.objects.create(
        user=user,
        name=name,
        type=skill_type,
        reason=data.get("reason", ""),
        timeline=data.get("timeline", "")
    )

    return JsonResponse({
        "success": True,
        "skill": {
            "id": skill.id,
            "name": skill.name,
            "type": skill.type
        }
    })

# ===========================
# DASHBOARD - ROADMAPS
# ===========================
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Roadmap, Activity
from .serializers import RoadmapSerializer, ActivitySerializer

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.authentication import BasicAuthentication

@api_view(["GET", "POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def roadmaps(request):

    if request.method == "GET":
        user_id = request.GET.get("user_id")
        qs = Roadmap.objects.filter(user_id=user_id).order_by("-created_at")
        serializer = RoadmapSerializer(qs, many=True)
        return Response(serializer.data)

    if request.method == "POST":

        data = request.data.copy()

        # normalize skill name (python -> Python)
        if "skill" in data and isinstance(data["skill"], str):
            data["skill"] = data["skill"].strip().title()

        serializer = RoadmapSerializer(data=data)

        if serializer.is_valid():
            serializer.save(user_id=data.get("user_id"))
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)

@api_view(["PATCH"])
@authentication_classes([])
@permission_classes([AllowAny])
def roadmap_update(request, roadmap_id):

    roadmap = get_object_or_404(Roadmap, id=roadmap_id)
    serializer = RoadmapSerializer(roadmap, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors, status=400)


# ===========================
# DASHBOARD - ACTIVITIES
# ===========================
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Activity
from .serializers import ActivitySerializer

@api_view(["GET", "POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def activities(request):

    if request.method == "GET":
        user_id = request.GET.get("user_id")

        qs = (
            Activity.objects
            .filter(user_id=user_id)
            .order_by("-created_at")[:10]
        )

        serializer = ActivitySerializer(qs, many=True)
        return Response(serializer.data)

    if request.method == "POST":
        user_id = request.data.get("user_id")
        text = request.data.get("text")

        if not user_id or not text:
            return Response(
                {"error": "user_id and text are required"},
                status=400
            )

        activity = Activity.objects.create(
            user_id=user_id,
            text=text
        )

        serializer = ActivitySerializer(activity)
        return Response(serializer.data, status=201)

#dashboard-today focus and cal
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Event
from .serializers import EventSerializer

@api_view(["GET", "POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def events(request):

    if request.method == "GET":
        user_id = request.GET.get("user_id")
        qs = Event.objects.filter(user_id=user_id).order_by("date")
        return Response(EventSerializer(qs, many=True).data)

    if request.method == "POST":
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

@api_view(["PATCH"])
@authentication_classes([])
@permission_classes([AllowAny])
def event_update(request, event_id):

    event = get_object_or_404(Event, id=event_id)
    serializer = EventSerializer(event, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)

#dasboard-from banner to skill comparison
from django.http import JsonResponse
from django.utils.timezone import now
from datetime import timedelta
from .models import Roadmap, Event

def banner_message(request):
    user_id = request.GET.get("user_id")
    today = now().date()

    active_roadmaps = Roadmap.objects.filter(user_id=user_id, completed=False)
    todays_events = Event.objects.filter(
        user_id=user_id,
        date=today,
        completed=False,
        type__in=["study", "exchange"]
    )

    if not active_roadmaps.exists():
        message = "No active roadmap — ready to plan your next skill?"
    elif not todays_events.exists():
        message = "Nothing planned today — small steps still count 🌱"
    else:
        count = todays_events.count()
        message = f"You have {count} thing{'s' if count > 1 else ''} planned today"

    return JsonResponse({ "message": message })


def weekly_summary(request):
    user_id = request.GET.get("user_id")
    week_ago = now().date() - timedelta(days=7)

    completed_count = Event.objects.filter(
        user_id=user_id,
        completed=True,
        date__gte=week_ago
    ).count()

    return JsonResponse({ "completed_this_week": completed_count })


def skill_timeline(request):
    user_id = request.GET.get("user_id")
    today = now().date()

    roadmaps = Roadmap.objects.filter(user_id=user_id).order_by("start_date")

    timeline = []
    for r in roadmaps:
        if r.completed:
            status = "completed"
        elif r.start_date and r.start_date > today:
            status = "upcoming"
        else:
            status = "active"

        timeline.append({
            "id": r.id,
            "skill": r.skill,
            "start_date": r.start_date,
            "status": status
        })

    return JsonResponse(timeline, safe=False)
from .models import Exchange

from django.http import JsonResponse
from api.models import Exchange, Event

def exchange_stats(request):
    user_id = request.GET.get("user_id")

    if not user_id:
        return JsonResponse({"error": "user_id required"}, status=400)

    # 🗓 Upcoming exchanges from CALENDAR
    upcoming = Event.objects.filter(
        user_id=user_id,
        type="exchange",
        completed=False
    ).count()

    # 🤝 Completed exchanges from EXCHANGE ROOM
    completed = Exchange.objects.filter(
        user_a_id=user_id,
        status="completed"
    ).count() + Exchange.objects.filter(
        user_b_id=user_id,
        status="completed"
    ).count()

    return JsonResponse({
        "upcoming": upcoming,
        "completed": completed
    })


def skill_comparison(request):
    user_id = request.GET.get("user_id")

    completed = Roadmap.objects.filter(user_id=user_id, completed=True).order_by("-id")
    active = Roadmap.objects.filter(user_id=user_id, completed=False).first()

    if not completed.exists() or not active:
        return JsonResponse({ "locked": True })

    last = completed.first()

    return JsonResponse({
        "past_skill": last.skill,
        "past_steps": len(last.steps),
        "current_skill": active.skill,
        "current_steps": len(active.steps)
    })
from django.utils import timezone
from datetime import timedelta
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Activity, Reflection


@api_view(["GET"])
@permission_classes([AllowAny])
def weekly_reflection_status(request):
    user_id = request.GET.get("user_id")

    if not user_id:
        return Response({"error": "user_id required"}, status=400)

    oldest_activity = (
        Activity.objects
        .filter(user_id=user_id)
        .order_by("created_at")
        .first()
    )

    if not oldest_activity:
        return Response({
            "unlocked": False,
            "days_left": 7,
            "latest": None
        })

    days_passed = (timezone.now() - oldest_activity.created_at).days

    if days_passed < 7:
        return Response({
            "unlocked": False,
            "days_left": 7 - days_passed,
            "latest": None
        })

    latest_reflection = (
        Reflection.objects
        .filter(user_id=user_id)
        .order_by("-created_at")
        .first()
    )

    return Response({
        "unlocked": True,
        "days_left": 0,
        "latest": latest_reflection.text if latest_reflection else "You stayed consistent this week and progressed in your learning journey."
    })


@api_view(["POST"])
@permission_classes([AllowAny])
def save_weekly_reflection(request):
    user_id = request.data.get("user_id")
    text = request.data.get("text")
    week = request.data.get("week")

    if not user_id or not text or not week:
        return Response({"error": "user_id, text, week required"}, status=400)

    reflection = Reflection.objects.create(
        user_id=user_id,
        text=text,
        week=week
    )

    return Response({
        "status": "saved",
        "id": reflection.id,
        "week": week,
        "text": text
    })
# dashbaord - create skill 
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny

@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def create_skill(request):

    user_id = request.data.get("user_id")
    name = request.data.get("name")
    type = request.data.get("type")

    if not user_id or not name or not type:
        return Response({"error": "Missing fields"}, status=400)

    user = get_object_or_404(User, id=user_id)

    # Save skill in Skill table
    skill = Skill.objects.create(
        user=user,
        name=name,
        type=type
    )

    # 🔥 ALSO update connect card
    profile, created = UserProfile.objects.get_or_create(user=user)

    if name not in profile.skills:
        profile.skills.append(name)
        profile.save()

    return Response({
        "id": skill.id,
        "name": skill.name,
        "type": skill.type
    }, status=201)


# explore/from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .models import Post, Like, Comment, SavedPost, Message
import json


# ------------------------
# Helpers
# ------------------------

def serialize_post(post, user=None):
    user = user if user and user.is_authenticated else None

    return {
        "id": post.id,
        "author": post.author.id,                     # ✅ frontend expects "author"
        "author_name": post.author.username,          # ✅ frontend expects this
        "author_headline": "",                        # ✅ keep empty if no profile
        "skill": post.skill,
        "text": post.text,
        "image": post.image.url if post.image else None,
        "created_at": post.created_at.isoformat(),    # ✅ frontend expects created_at
        "likes_count": Like.objects.filter(post=post).count(),
        "liked_by_me": bool(user and Like.objects.filter(post=post, user=user).exists()),
        "comments_count": Comment.objects.filter(post=post).count(),
        "saved_by_me": bool(user and SavedPost.objects.filter(post=post, user=user).exists()),
    }


# ------------------------
# Feed
# ------------------------

def get_posts(request):
    posts = Post.objects.all().order_by("-created_at")
    data = [serialize_post(p, request.user) for p in posts]
    return JsonResponse(data, safe=False, status=200)

# ------------------------
# Like
# ------------------------
@csrf_exempt
def toggle_like(request, post_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    user_id = data.get("user_id")
    if not user_id:
        return JsonResponse({"error": "user_id required"}, status=401)

    user = get_object_or_404(User, id=user_id)
    post = get_object_or_404(Post, id=post_id)

    like = Like.objects.filter(user=user, post=post).first()
    if like:
        like.delete()
        return JsonResponse({"liked": False})

    Like.objects.create(user=user, post=post)
    return JsonResponse({"liked": True})

# ------------------------
# Comment
# ------------------------
@csrf_exempt
def add_comment(request, post_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    user_id = data.get("user_id")
    text = data.get("text", "").strip()

    if not user_id:
        return JsonResponse({"error": "user_id required"}, status=401)

    if not text:
        return JsonResponse({"error": "Comment cannot be empty"}, status=400)

    user = get_object_or_404(User, id=user_id)
    post = get_object_or_404(Post, id=post_id)

    Comment.objects.create(user=user, post=post, text=text)
    return JsonResponse({"success": True}, status=201)

# ------------------------
# Get Comments
# ------------------------
def get_comments(request, post_id):
    comments = Comment.objects.filter(post_id=post_id).select_related("user").order_by("-id")

    data = [
        {
            "id": c.id,
            "text": c.text,
            "username": c.user.username,
            "user_id": c.user.id,
        }
        for c in comments
    ]

    return JsonResponse(data, safe=False, status=200)

# ------------------------
# Save
# ------------------------
@csrf_exempt
def toggle_save(request, post_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    data = json.loads(request.body or "{}")
    user_id = data.get("user_id")
    if not user_id:
        return JsonResponse({"error": "user_id required"}, status=401)

    user = get_object_or_404(User, id=user_id)
    post = get_object_or_404(Post, id=post_id)

    obj = SavedPost.objects.filter(user=user, post=post).first()
    if obj:
        obj.delete()
        return JsonResponse({"saved": False})

    SavedPost.objects.create(user=user, post=post)
    return JsonResponse({"saved": True})

# ------------------------
# Create Post
# ------------------------

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .models import Post
@csrf_exempt
def create_post(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    user_id = request.POST.get("user_id")
    text = request.POST.get("text", "").strip()
    skill = request.POST.get("skill", "Self Learning")
    image = request.FILES.get("image")

    if not user_id:
        return JsonResponse({"error": "user_id required"}, status=400)
    if not text:
        return JsonResponse({"error": "Text is required"}, status=400)

    user = get_object_or_404(User, id=user_id)

    post = Post.objects.create(
        author=user,
        text=text,
        skill=skill,
        image=image
    )

    return JsonResponse({
        "id": post.id,
        "text": post.text,
        "skill": post.skill,
        "image": post.image.url if post.image else None,
        "authorId": user.id,
        "authorName": user.username,
        "createdAt": post.created_at.isoformat(),
        "likes": 0,
        "comments": 0,
    }, status=201)

# ------------------------
# Delete Post
# ------------------------

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Post

@csrf_exempt   # 🔥 important for frontend POST
@login_required
def delete_post(request, post_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    post = get_object_or_404(Post, id=post_id)

    if post.author != request.user:
        return JsonResponse({"error": "You can delete only your own posts"}, status=403)

    post.delete()
    return JsonResponse({"success": True})

# ------------------------
# Saved Posts
# ------------------------

def get_saved_posts(request):
    user = request.user if request.user.is_authenticated else None
    if not user:
        return JsonResponse([], safe=False, status=200)

    saved = SavedPost.objects.filter(user=user).select_related("post", "post__author")

    data = [
        {
            "id": s.post.id,
            "authorName": s.post.author.username,
            "text": s.post.text,
            "image": s.post.image.url if s.post.image else None,
        }
        for s in saved
    ]

    return JsonResponse(data, safe=False, status=200)


# ------------------------
# Debug
# ------------------------

def whoami(request):
    return JsonResponse({
        "is_authenticated": request.user.is_authenticated,
        "user": request.user.username if request.user.is_authenticated else None
    })
from django.shortcuts import get_object_or_404
from .models import Comment
#delete comment
@csrf_exempt
def delete_comment(request, comment_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    comment = get_object_or_404(Comment, id=comment_id)
    comment.delete()
    return JsonResponse({"success": True}, status=200)

#health check
from django.http import JsonResponse

def health(request):
    return JsonResponse({"ok": True})

#CONNECT
#user profile
from django.http import JsonResponse
from api.models import UserProfile

def connect_people(request):
    from django.contrib.auth.models import User

    users = User.objects.all()

    data = []

    for u in users:
        profile, _ = UserProfile.objects.get_or_create(user=u)

        data.append({
            "id": u.id,
            "name": u.username,
            "subtitle": profile.subtitle,
            "location": profile.location,
            "skills": profile.skills,
            "verified": profile.verified,
            "featured": profile.featured,
            "rating": profile.rating,
        })

    return JsonResponse(data, safe=False)

#send request
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.models import User
from api.models import ExchangeRequest
import json
@csrf_exempt
def send_exchange_request(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)
    except Exception as e:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    from_user_id = data.get("from_user_id")
    to_user_id = data.get("to_user_id")

    if not from_user_id or not to_user_id:
        return JsonResponse({"error": "Both users required"}, status=400)

    if from_user_id == to_user_id:
        return JsonResponse({"error": "Cannot request yourself"}, status=400)

    try:
        from_user = User.objects.get(id=from_user_id)
        to_user = User.objects.get(id=to_user_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    req, created = ExchangeRequest.objects.get_or_create(
        from_user=from_user,
        to_user=to_user,
        defaults={"status": "pending"}
    )

    return JsonResponse({
        "success": True,
        "created": created,
        "status": req.status
    })


#sent request

def my_sent_requests(request, user_id):
    qs = ExchangeRequest.objects.filter(from_user_id=user_id)
    data = [
        {
            "to_user": r.to_user.username,
            "status": r.status
        } for r in qs
    ]
    return JsonResponse(data, safe=False)

#quick matches
def quick_matches(request, user_id):
    profiles = UserProfile.objects.filter(verified=True)[:6]

    data = [{
        "id": p.user.id,
        "name": p.user.username,
        "rating": p.rating
    } for p in profiles]

    return JsonResponse(data, safe=False)

#send target
def sent_targets(request, user_id):
    qs = ExchangeRequest.objects.filter(from_user_id=user_id).values_list("to_user_id", flat=True)
    return JsonResponse(list(qs), safe=False)

#EXCHANGE ROOM
@csrf_exempt
def create_exchange(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    user_a = data.get("user_a")
    user_b = data.get("user_b")
    skill_a = data.get("skill_a")
    skill_b = data.get("skill_b")
    date = data.get("date")
    time = data.get("time")

    if not all([user_a, user_b, skill_a, skill_b, date, time]):
        return JsonResponse({"error": "Missing required fields"}, status=400)

    # 🔒 Prevent duplicate exchanges between same users
    existing = Exchange.objects.filter(
        Q(user_a_id=user_a, user_b_id=user_b) |
        Q(user_a_id=user_b, user_b_id=user_a),
        status="pending"
    ).first()

    if existing:
        return JsonResponse({
            "id": existing.id,
            "status": existing.status,
            "message": "Exchange already exists"
        })

    exchange = Exchange.objects.create(
        user_a_id=user_a,
        user_b_id=user_b,
        skill_a=skill_a,
        skill_b=skill_b,
        date=date,
        time=time,
        status="pending"
    )

    return JsonResponse({
        "id": exchange.id,
        "status": exchange.status
    })

#send message api
@csrf_exempt
def send_exchange_message(request):

    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    data = json.loads(request.body)

    msg = ExchangeMessage.objects.create(
        exchange_id=data["exchange_id"],
        sender_id=data["sender_id"],
        message=data["message"]
    )

    return JsonResponse({"success": True, "id": msg.id})

#complete exchange
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Exchange, Certificate


@csrf_exempt
def complete_exchange(request, exchange_id):

    try:
        exchange = Exchange.objects.get(id=exchange_id)
    except Exchange.DoesNotExist:
        return JsonResponse({"error": "Exchange not found"}, status=404)

    # prevent completing twice
    if exchange.status == "completed":
        return JsonResponse({"message": "Exchange already completed"})

    # mark completed
    exchange.status = "completed"
    exchange.save()

    # generate certificates for both users
    Certificate.objects.create(
        user=exchange.user_a,
        certificate_id=f"EX-{exchange.id}-A",
        type="exchange",
        skill=exchange.skill_a
    )

    Certificate.objects.create(
        user=exchange.user_b,
        certificate_id=f"EX-{exchange.id}-B",
        type="exchange",
        skill=exchange.skill_b
    )

    return JsonResponse({
        "success": True,
        "exchange_id": exchange.id,
        "certificates_created": True
    })

#submit review

@csrf_exempt
def submit_review(request):

    data = json.loads(request.body)

    exchange = Exchange.objects.get(id=data["exchange_id"])
    reviewer_id = data["reviewer_id"]

    # determine who is being reviewed
    if exchange.user_a_id == reviewer_id:
        reviewed_user = exchange.user_b
    else:
        reviewed_user = exchange.user_a

    ExchangeRating.objects.create(
        exchange=exchange,
        reviewer_id=reviewer_id,
        reviewed_user=reviewed_user,
        rating=data["rating"],
        feedback=data.get("feedback", "")
    )

    return JsonResponse({"success": True})

#complete exchange event
@csrf_exempt
def complete_exchange_event(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    data = json.loads(request.body)
    user_id = data.get("user_id")
    exchange_id = data.get("exchange_id")

    if not user_id or not exchange_id:
        return JsonResponse({"error": "Missing fields"}, status=400)

    # mark related calendar event as completed
    Event.objects.filter(user_id=user_id, exchange_id=exchange_id).update(completed=True)

    return JsonResponse({"success": True})

#MESSAGE PAGE

@csrf_exempt
@login_required
def send_message(request, user_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    body = json.loads(request.body or "{}")
    content = body.get("content", "")

    sender = request.user
    receiver = get_object_or_404(User, id=user_id)

    if sender.id == receiver.id:
        return JsonResponse({"error": "Cannot message yourself"}, status=400)

    Message.objects.create(
        sender=sender,
        receiver=receiver,
        content=content
    )

    return JsonResponse({"ok": True})
    
@login_required
@csrf_exempt
def mark_seen(request, msg_id):
    Message.objects.filter(id=msg_id, receiver=request.user).update(seen=True)
    return JsonResponse({"ok": True})

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from api.models import Message
from django.contrib.auth.models import User
from django.db.models import Q, Max

@login_required
def get_conversations(request):

    me = request.user

    users = User.objects.exclude(id=me.id)

    data = []

    for u in users:

        last_msg = Message.objects.filter(
            Q(sender=me, receiver=u) | Q(sender=u, receiver=me)
        ).order_by("-timestamp").first()

        unread = Message.objects.filter(
            sender=u,
            receiver=me,
            seen=False
        ).count()

        data.append({
            "id": u.id,
            "name": u.username,   # always show username
            "lastMessage": last_msg.content if last_msg else "Start a conversation",
            "unread": unread,
            "lastActive": "Online"
        })

    return JsonResponse(data, safe=False)

@login_required
def chat_messages(request, user_id):

    if int(user_id) == request.user.id:
        return JsonResponse([], safe=False)

    me = request.user
    other = User.objects.get(id=user_id)

    qs = Message.objects.filter(
        Q(sender=me, receiver=other) | Q(sender=other, receiver=me)
    ).order_by("timestamp")

    data = []   # 🔥 THIS LINE IS MISSING IN YOUR FILE

    for m in qs:
        data.append({
    "id": m.id,
    "sender": "me" if m.sender == me else "them",
    "sender_id": m.sender.id,
    "content": m.content,
    "time": m.timestamp.isoformat(),
    "seen": m.seen,
    "post_id": m.post.id if m.post else None,
    "request_from": m.request_from
    })

    return JsonResponse(data, safe=False)

@csrf_exempt
def share_post(request, post_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    data = json.loads(request.body or "{}")
    user_id = data.get("user_id")
    to_user_id = data.get("to_user_id")

    user = get_object_or_404(User, id=user_id)
    to_user = get_object_or_404(User, id=to_user_id)
    post = get_object_or_404(Post, id=post_id)

    Message.objects.create(
        sender=user,
        receiver=to_user,
        content="Shared a post",   # 🔥 DO NOT PUT POST TEXT HERE
        post=post                 # 🔥 THIS IS WHAT MAKES IT CLICKABLE
    )

    return JsonResponse({"success": True})

#PROGRESS PAGE
from django.contrib.auth.models import User
from django.http import JsonResponse
from .models import Roadmap, Event, Activity, Certificate

def progress_api(request):

    user_id = request.GET.get("user_id")

    if not user_id:
        return JsonResponse({"error": "user_id required"}, status=400)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    sessions = Event.objects.filter(
        user_id=user_id,
        type="study",
        completed=True
    ).count()

    active_exchanges = Event.objects.filter(
        user_id=user_id,
        type="exchange",
        completed=False
    ).count()

    skills_learned = Roadmap.objects.filter(
        user_id=user_id,
        completed=True
    ).count()

    total_exchanges = (
        Exchange.objects.filter(user_a_id=user_id, status="completed").count()
        + Exchange.objects.filter(user_b_id=user_id, status="completed").count()
    )

    roadmaps_data = []

    for r in Roadmap.objects.filter(user_id=user_id):

        total_steps = len(r.steps) if isinstance(r.steps, list) else 0
        completed_steps = total_steps if r.completed else 0

        roadmaps_data.append({
            "id": r.id,
            "skill": r.skill,
            "steps": total_steps,
            "completed_steps": completed_steps,
            "completed": r.completed,
            "updated_at": getattr(r, "updated_at", r.id)
        })

    activity_data = list(
        Activity.objects
        .filter(user_id=user_id)
        .order_by("-created_at")[:10]
        .values("text", "created_at")
    )

    certificates = list(
        Certificate.objects
        .filter(user_id=user_id)
        .values("certificate_id", "type", "skill", "created_at")
    )
    profile, _ = UserProfile.objects.get_or_create(user_id=user_id)
    return JsonResponse({
        "sessions": sessions,
        "active_exchanges": active_exchanges,
        "skills_learned": skills_learned,
        "total_exchanges": total_exchanges,
        "streak": skills_learned,
        "roadmaps": roadmaps_data,
        "activity": activity_data,
        "certificates": certificates,
        "profile_views": profile.profile_views,
    })

#certificates 
@csrf_exempt
def certificates_api(request):

    if request.method == "POST":

        data = json.loads(request.body or "{}")

        user_id = data.get("user_id")
        certificate_id = data.get("certificate_id")
        cert_type = data.get("type")
        skill = data.get("skill")

        if not user_id:
            return JsonResponse({"error": "user_id required"}, status=400)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)

        cert = Certificate.objects.create(
            user=user,
            certificate_id=certificate_id,
            type=cert_type,
            skill=skill
        )

        return JsonResponse({
            "id": cert.id,
            "certificate_id": cert.certificate_id,
            "type": cert.type,
            "skill": cert.skill,
            "created_at": cert.created_at
        })

    if request.method == "GET":

        user_id = request.GET.get("user_id")

        if not user_id:
            return JsonResponse([], safe=False)

        certs = Certificate.objects.filter(user_id=user_id).values(
            "certificate_id", "type", "skill", "created_at"
        )

        return JsonResponse(list(certs), safe=False)

from django.http import JsonResponse
from api.models import Exchange
from django.contrib.auth.models import User

from django.db.models import Q

def exchanges_api(request):
    user_id = request.GET.get("user_id")

    if not user_id:
        return JsonResponse([], safe=False)

    exchanges = Exchange.objects.filter(
        Q(user_a_id=user_id) | Q(user_b_id=user_id),
        status="completed"
    )

    data = []

    for e in exchanges:

        # ensure CURRENT USER is always A
        if str(e.user_a_id) == str(user_id):
            user_a = e.user_a
            user_b = e.user_b
            skill_a = e.skill_a
            skill_b = e.skill_b
        else:
            user_a = e.user_b
            user_b = e.user_a
            skill_a = e.skill_b
            skill_b = e.skill_a

        data.append({
            "id": e.id,
            "user_a_id": user_a.id,
            "user_b_id": user_b.id,
            "user_a_name": user_a.username,
            "user_b_name": user_b.username,
            "skill_a": skill_a,
            "skill_b": skill_b,
            "status": e.status,
            "date": e.date,
            "time": e.time
        })

    return JsonResponse(data, safe=False)

@csrf_exempt
def get_exchange_messages(request, exchange_id):
    if request.method != "GET":
        return JsonResponse({"error": "GET required"}, status=405)

    messages = ExchangeMessage.objects.filter(
        exchange_id=exchange_id
    ).order_by("id")

    data = [
        {
            "id": m.id,
            "sender_id": m.sender_id,
            "message": m.message,
        }
        for m in messages
    ]

    return JsonResponse(data, safe=False)

from django.http import JsonResponse
from django.db.models import Avg, Q
from django.contrib.auth.models import User
from .models import Roadmap, Exchange, Event, ExchangeRating


def profile_stats(request):
    user_id = request.GET.get("user_id")

    if not user_id:
        return JsonResponse({"error": "user_id required"}, status=400)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    completed_roadmaps = Roadmap.objects.filter(user_id=user_id, completed=True).count()

    completed_exchanges = (
        Exchange.objects.filter(user_a_id=user_id, status="completed").count() +
        Exchange.objects.filter(user_b_id=user_id, status="completed").count()
    )

    upcoming_exchanges = Event.objects.filter(
        user_id=user_id,
        type="exchange",
        completed=False
    ).count()

    # ✅ Ratings received by this user (not ratings they gave)
    ratings_qs = ExchangeRating.objects.filter(
    Q(exchange__user_a_id=user_id) |
    Q(exchange__user_b_id=user_id)
     ).exclude(
        reviewer_id=user_id
     )

    ratings_count = ratings_qs.count()
    average_rating = ratings_qs.aggregate(avg=Avg("rating"))["avg"] or 0

    from .models import Certificate

    certificates_count = Certificate.objects.filter(user_id=user_id).count()

    return JsonResponse({
    "completed_roadmaps": completed_roadmaps,
    "completed_exchanges": completed_exchanges,
    "certificates": certificates_count,
    "skills": completed_roadmaps,
    "streak": completed_roadmaps,
    "ratings_count": ratings_count,
    "average_rating": round(average_rating, 1),
    "upcoming_exchanges": upcoming_exchanges
  })
def profile_certificates(request):

    user_id = request.GET.get("user_id")

    if not user_id:
        return JsonResponse([], safe=False)

    certs = Certificate.objects.filter(user_id=user_id)

    data = []

    for c in certs:
        data.append({
            "title": f"{c.skill or 'Skill'} Certificate",
            "type": c.type,
            "issued_on": c.created_at,
            "file_url": f"http://127.0.0.1:8000/api/certificate/download/{c.certificate_id}/"
        })

    return JsonResponse(data, safe=False)

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
import json

@csrf_exempt
def user_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == "GET":
        return JsonResponse({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "date_joined": user.date_joined
        })

    if request.method == "PATCH":
        data = json.loads(request.body or "{}")
        user.username = data.get("username", user.username)
        user.save()

        return JsonResponse({
            "success": True,
            "id": user.id,
            "username": user.username
        })

    return JsonResponse({"error": "Method not allowed"}, status=405)

from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Report

@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def submit_report(request):
    reported_user_val = request.data.get("reported_user")
    reported_by = request.data.get("reported_by")

    # ✅ Convert username to user id if needed
    if isinstance(reported_user_val, str):
        try:
            reported_user = User.objects.get(username=reported_user_val)
            reported_user_id = reported_user.id
        except User.DoesNotExist:
            return Response({"error": "Reported user not found"}, status=404)
    else:
        reported_user_id = reported_user_val

    Report.objects.create(
        reported_user_id=reported_user_id,
        reported_by_id=reported_by,
        report_type=request.data.get("report_type"),
        report_location=request.data.get("report_location"),
        description=request.data.get("description")
    )

    return Response({"message": "Report submitted"}, status=201)

@api_view(["POST"])
def submit_exchange_review(request):
    exchange_id = request.data.get("exchange_id")
    reviewer_id = request.data.get("reviewer_id")
    rating = request.data.get("rating")
    feedback = request.data.get("feedback", "")

    exchange = Exchange.objects.get(id=exchange_id)
    reviewed_user = exchange.user_b if exchange.user_a_id == reviewer_id else exchange.user_a

    ExchangeRating.objects.create(
        exchange_id=exchange_id,
        reviewer_id=reviewer_id,
        reviewed_user=reviewed_user,
        rating=rating,
        feedback=feedback
    )

    return Response({"success": True})

@csrf_exempt
def system_message(request):

    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    data = json.loads(request.body or "{}")

    sender_id = data.get("sender_id")
    receiver_id = data.get("receiver_id")
    text = data.get("text")
    request_from = data.get("request_from", None)

    if not sender_id or not receiver_id or not text:
        return JsonResponse({"error": "sender_id, receiver_id, text required"}, status=400)

    sender = get_object_or_404(User, id=sender_id)
    receiver = get_object_or_404(User, id=receiver_id)

    Message.objects.create(
        sender=sender,
        receiver=receiver,
        content=text,
        request_from=request_from
    )

    return JsonResponse({"success": True})

@csrf_exempt
def accept_request(request):

    data = json.loads(request.body)

    from_user_id = data.get("from_user_id")
    to_user_id = data.get("to_user_id")

    ExchangeRequest.objects.filter(
        from_user_id=from_user_id,
        to_user_id=to_user_id
    ).update(status="accepted")

    # 🔥 remove buttons from message
    Message.objects.filter(
    sender_id=from_user_id,
    receiver_id=to_user_id,
    request_from=from_user_id
    ).update(
       request_from=None,
    content="Your skill exchange request was accepted."
    )

    return JsonResponse({"success": True})


@csrf_exempt
def decline_request(request):

    data = json.loads(request.body)

    from_user_id = data.get("from_user_id")
    to_user_id = data.get("to_user_id")

    ExchangeRequest.objects.filter(
        from_user_id=from_user_id,
        to_user_id=to_user_id
    ).update(status="rejected")

    Message.objects.filter(
    sender_id=from_user_id,
    receiver_id=to_user_id,
    request_from=from_user_id
    ).update(
       request_from=None,
       content="Your skill exchange request was declined."
    )

    return JsonResponse({"success": True})

@csrf_exempt
def create_profile(request):

    data = json.loads(request.body)

    user_id = data.get("user_id")
    subtitle = data.get("subtitle")
    location = data.get("location")
    skills = data.get("skills")

    user = User.objects.get(id=user_id)

    profile, created = UserProfile.objects.get_or_create(user=user)

    profile.subtitle = subtitle
    profile.location = location
    profile.skills = skills
    profile.save()

    return JsonResponse({
        "success": True,
        "created": created
    })

from django.db.models import Q

def user_reviews(request):

    user_id = request.GET.get("user_id")

    reviews = ExchangeRating.objects.filter(
        reviewed_user_id=user_id
    ).select_related("reviewer").order_by("-id")

    data = []

    for r in reviews:
        data.append({
            "rating": r.rating,
            "feedback": r.feedback,
            "reviewer": r.reviewer.username
        })

    return JsonResponse(data, safe=False)

from django.http import FileResponse
import os
from django.conf import settings

def download_certificate(request, cert_id):

    cert = Certificate.objects.filter(certificate_id=cert_id).first()

    if not cert:
        return JsonResponse({"error": "Certificate not found"}, status=404)

    folder = os.path.join(settings.MEDIA_ROOT, "certificates")

    files = os.listdir(folder)

    if not files:
        return JsonResponse({"error": "No certificate template found"}, status=404)

    file_path = os.path.join(folder, files[0])

    return FileResponse(
        open(file_path, "rb"),
        as_attachment=True,
        filename=f"SkillSwap-Certificate-{cert.certificate_id}.pdf"
    )

@api_view(["POST"])
def increment_profile_view(request):

    user_id = request.data.get("user_id")

    if not user_id:
        return Response({"error": "user_id required"}, status=400)

    profile, created = UserProfile.objects.get_or_create(user_id=user_id)

    profile.profile_views = (profile.profile_views or 0) + 1
    profile.save()

    return Response({"success": True, "views": profile.profile_views})