# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
# from posts.models import Comment  # Import your Comment model
# from asgiref.sync import sync_to_async

# class CommentConsumer(AsyncWebsocketConsumer):
#     connected_clients = set()  # Track all connected clients

#     async def connect(self):
#         """Connect WebSocket and add to connected clients."""
#         self.connected_clients.add(self)
#         await self.accept()

#     async def disconnect(self, close_code):
#         """Remove from connected clients on disconnect."""
#         self.connected_clients.discard(self)

#     async def receive(self, text_data):
#         """Handle incoming message, save to DB, and broadcast to clients."""
#         data = json.loads(text_data)
#         message = data["message"]
#         username = data["username"]
#         post_id = self.scope['url_route']['kwargs']['post_id']

#         # Save to database
#         await self.save_comment_to_db(message, username, post_id)

#         # Broadcast to all connected WebSocket clients
#         for client in self.connected_clients:
#             await client.send(text_data=json.dumps({
#                 "message": message,
#                 "username": username
#             }))

#     @sync_to_async
#     def save_comment_to_db(self, message, username, post_id):
#         """Save comment to database asynchronously."""
#         Comment.objects.create(post_id=post_id, message=message, username=username)
