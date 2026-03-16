from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import Message

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        try:
            me = User.objects.get(username="harini")   # 🔥 CHANGE to your login username
        except User.DoesNotExist:
            self.stdout.write("User not found")
            return

        other = User.objects.exclude(id=me.id).first()
        if not other:
            self.stdout.write("Create another user first")
            return

        Message.objects.create(sender=me, receiver=other, content="Mock hello 👋")
        Message.objects.create(sender=other, receiver=me, content="Mock reply 🙂")

        self.stdout.write(self.style.SUCCESS("Seeded messages for current user"))
