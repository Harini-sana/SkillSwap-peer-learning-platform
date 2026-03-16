from django.urls import path
from . import views

# Explicit imports for exchange features
from .views import (
    connect_people,
    send_exchange_request,
    my_sent_requests,
    create_exchange,
    send_exchange_message,
    complete_exchange,
    submit_review,
    complete_exchange_event,
)

urlpatterns = [
    # AUTH
    path("signup/", views.signup),
    path("login/", views.login),
    path("reset-password/", views.reset_password),

    # NEWSLETTER & CONTACT
    path("newsletter/", views.subscribe_newsletter),
    path("contact/", views.submit_contact),

    # SKILLS
    path("skills/add/", views.add_skill),
    path("skills/", views.create_skill),

    # DASHBOARD
    path("roadmaps/", views.roadmaps),
    path("roadmaps/<int:roadmap_id>/", views.roadmap_update),
    path("activities/", views.activities),

    path("events/", views.events),
    path("events/<int:event_id>/", views.event_update),

    path("dashboard/banner/", views.banner_message),
    path("dashboard/weekly/", views.weekly_summary),
    path("dashboard/timeline/", views.skill_timeline),
    path("dashboard/exchange-stats/", views.exchange_stats),
    path("dashboard/comparison/", views.skill_comparison),

    path("dashboard/reflection/", views.weekly_reflection_status),
    path("dashboard/reflection/save/", views.save_weekly_reflection),

    # 👤 USER PROFILE (ONLY ONE ROUTE – FIXED)
    path("users/<int:user_id>/", views.user_detail),

    # EXPLORE / POSTS
    path("posts/", views.get_posts),
    path("posts/create/", views.create_post),
    path("posts/<int:post_id>/delete/", views.delete_post),

    path("posts/<int:post_id>/like/", views.toggle_like),
    path("posts/<int:post_id>/comment/", views.add_comment),
    path("posts/<int:post_id>/save/", views.toggle_save),
    path("posts/<int:post_id>/share/", views.share_post),
    path("posts/<int:post_id>/comments/", views.get_comments),

    path("comments/<int:comment_id>/delete/", views.delete_comment),
    path("posts/saved/", views.get_saved_posts),

    # HEALTH & DEBUG
    path("whoami/", views.whoami),
    path("health/", views.health),

    # CONNECT
    path("connect/people/", connect_people),
    path("connect/request/", send_exchange_request),
    path("connect/sent/<int:user_id>/", my_sent_requests),
    path("connect/accept/", views.accept_request),
    path("connect/decline/", views.decline_request),
    path("messages/system/", views.system_message),
    path("connect/create-profile/", views.create_profile),

    # EXCHANGE ROOM
    path("exchange/create/", create_exchange),
    path("exchange/message/", send_exchange_message),
    path("exchange/<int:exchange_id>/messages/", views.get_exchange_messages),  # ✅ ADD THIS
    path("exchange/<int:exchange_id>/complete/", complete_exchange),
    path("exchange/review/", submit_review),

    # 💬 CHAT
    path("chat/conversations/", views.get_conversations),
    path("chat/<int:user_id>/messages/", views.chat_messages),
    path("chat/<int:user_id>/send/", views.send_message),
    path("chat/<int:msg_id>/seen/", views.mark_seen),

    # PROGRESS
    path("progress/", views.progress_api),
    path("exchanges/", views.exchanges_api),
    path("certificates/", views.certificates_api),

    # PROFILE STATS & CERTIFICATES
    path("profile/stats/", views.profile_stats),
    path("profile/reviews/", views.user_reviews),
    path("profile/certificates/", views.profile_certificates),
    path("report/", views.submit_report),
    path("certificate/download/<str:cert_id>/", views.download_certificate),
    path("profile/view/", views.increment_profile_view),
]