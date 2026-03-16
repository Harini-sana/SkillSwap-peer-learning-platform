from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
import json

from .models import Experience, Reflection


# ---------------------------
# AUTH HELPER (NO REDIRECTS)
# ---------------------------
def auth_required_json(request):
    if not request.user.is_authenticated:
        return JsonResponse(
            {"success": False, "error": "Authentication required"},
            status=401
        )
    return None


# ---------------------------
# DASHBOARD
# ---------------------------
@require_http_methods(["GET"])
def progress_dashboard(request):
    auth_error = auth_required_json(request)
    if auth_error:
        return auth_error

    experiences = Experience.objects.filter(user=request.user).order_by("-created_at")
    reflections = Reflection.objects.filter(user=request.user).order_by("-created_at")

    return JsonResponse({
        "success": True,
        "experiences": [
            {
                "id": e.id,
                "type": e.type,
                "skill": e.skill,
                "reason": e.reason,
                "timeline": e.timeline,
                "created_at": e.created_at.isoformat(),
            }
            for e in experiences
        ],
        "reflections": [
            {
                "id": r.id,
                "text": r.text,
                "created_at": r.created_at.isoformat(),
            }
            for r in reflections
        ],
    })


# ---------------------------
# ADD EXPERIENCE
# ---------------------------
@require_http_methods(["POST"])
def add_experience(request):
    auth_error = auth_required_json(request)
    if auth_error:
        return auth_error

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

    skill_type = data.get("type")
    skill = data.get("skill", "").strip()
    reason = data.get("reason", "").strip()
    timeline = data.get("timeline", "").strip()

    if skill_type not in ("offer", "request"):
        return JsonResponse({"success": False, "error": "Invalid type"}, status=400)

    if not skill:
        return JsonResponse({"success": False, "error": "Skill required"}, status=400)

    exp = Experience.objects.create(
        user=request.user,
        type=skill_type,
        skill=skill,
        reason=reason,
        timeline=timeline if skill_type == "request" else "",
    )

    return JsonResponse({"success": True, "id": exp.id})


# ---------------------------
# DELETE EXPERIENCE
# ---------------------------
@require_http_methods(["DELETE"])
def delete_experience(request, pk):
    auth_error = auth_required_json(request)
    if auth_error:
        return auth_error

    exp = get_object_or_404(Experience, pk=pk, user=request.user)
    exp.delete()

    return JsonResponse({"success": True})


# ---------------------------
# ADD REFLECTION
# ---------------------------
@require_http_methods(["POST"])
def add_reflection(request):
    auth_error = auth_required_json(request)
    if auth_error:
        return auth_error

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

    text = data.get("text", "").strip()
    if not text:
        return JsonResponse({"success": False, "error": "Text required"}, status=400)

    Reflection.objects.create(user=request.user, text=text)
    return JsonResponse({"success": True})
