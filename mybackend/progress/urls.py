from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.progress_dashboard),
    path("experience/", views.add_experience),
    path("experience/<int:pk>/", views.delete_experience),
    path("reflection/", views.add_reflection),
]
