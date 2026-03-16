from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import UserProfile

PEOPLE = [
    {
        "name": "Aria Patel",
        "subtitle": "Filmmaker & editor",
        "location": "Mumbai, IN • Online",
        "rating": 4.8,
        "skills": ["Video Editing", "Premiere Pro", "Color Grading"],
        "verified": True,
        "featured": True,
    },
    {
        "name": "Hannah Lee",
        "subtitle": "Digital Marketing Strategist",
        "location": "LA, US • Online",
        "rating": 4.6,
        "skills": ["SEO", "Content", "Branding"],
        "verified": False,
        "featured": False,
    },
    {
        "name": "Chen Wei",
        "subtitle": "Mandarin Tutor",
        "location": "Beijing, CN • Online",
        "rating": 4.9,
        "skills": ["Mandarin", "HSK Prep"],
        "verified": True,
        "featured": False,
    },
    {
        "name": "Lucas Martin",
        "subtitle": "Guitar & Music Theory",
        "location": "Berlin, DE • In-person",
        "rating": 4.7,
        "skills": ["Guitar", "Music Theory"],
        "verified": False,
        "featured": False,
    },
    {
        "name": "Sara Khan",
        "subtitle": "UI / UX Designer",
        "location": "Dubai, AE • Online",
        "rating": 4.8,
        "skills": ["Figma", "UX Research"],
        "verified": True,
        "featured": False,
    },
    {
        "name": "Ethan Brooks",
        "subtitle": "Frontend Developer",
        "location": "Toronto, CA • Online",
        "rating": 4.5,
        "skills": ["HTML", "CSS", "JavaScript"],
        "verified": False,
        "featured": False,
    },
    {
        "name": "Maria Gonzales",
        "subtitle": "Spanish Language Coach",
        "location": "Madrid, ES • Online",
        "rating": 4.9,
        "skills": ["Spanish", "Conversation"],
        "verified": True,
        "featured": True,
    },
    {
        "name": "Noah Kim",
        "subtitle": "Data Analyst",
        "location": "Seoul, KR • Online",
        "rating": 4.6,
        "skills": ["Python", "SQL", "Tableau"],
        "verified": False,
        "featured": False,
    },
    {
        "name": "Ava Thompson",
        "subtitle": "Content Writer",
        "location": "London, UK • Online",
        "rating": 4.7,
        "skills": ["Copywriting", "SEO"],
        "verified": True,
        "featured": False,
    },
    {
        "name": "Ravi Mehta",
        "subtitle": "Startup Mentor",
        "location": "Bangalore, IN • In-person",
        "rating": 4.8,
        "skills": ["Business Strategy", "Pitching"],
        "verified": True,
        "featured": True,
    },
    # 👉 You can continue adding the rest later (this is already enough for demo)
]


class Command(BaseCommand):
    help = "Seed people for Connect page"

    def handle(self, *args, **kwargs):
        for i, person in enumerate(PEOPLE, start=1):
            name = person["name"]
            email = f"connect{i}@demo.com"

            user, created = User.objects.get_or_create(
                username=name.replace(" ", "").lower(),
                defaults={"email": email},
            )

            if created:
                user.set_password("demo1234")
                user.save()

            UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    "subtitle": person["subtitle"],
                    "location": person["location"],
                    "skills": person["skills"],
                    "verified": person["verified"],
                    "featured": person["featured"],
                    "rating": person["rating"],
                },
            )

        self.stdout.write(self.style.SUCCESS("✅ Connect people seeded successfully"))
