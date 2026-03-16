import json
from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user_id = self.scope["url_route"]["kwargs"]["user_id"]
        self.room_group_name = f"chat_{self.user_id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )


    async def receive(self, text_data):

        print("🔥 WEBSOCKET RECEIVE CALLED")
        data = json.loads(text_data)

        message = data.get("message")
        receiver_id = data.get("receiver_id")
        sender_id = data.get("sender_id")

        print("WEBSOCKET DATA RECEIVED:", data)
        print("SENDER:", sender_id)
        print("RECEIVER:", receiver_id)

        if not receiver_id or not sender_id:
            return

        # send message to receiver
        await self.channel_layer.group_send(
            f"chat_{receiver_id}",
            {
                "type": "chat_message",
                "message": message,
                "sender_id": sender_id
            }
        )

        # send message back to sender (so sender sees it instantly)
        await self.channel_layer.group_send(
            f"chat_{sender_id}",
            {
                "type": "chat_message",
                "message": message,
                "sender_id": sender_id
            }
        )


    async def chat_message(self, event):
        await self.send(
            text_data=json.dumps({
                "message": event["message"],
                "sender_id": event["sender_id"]
            })
        )