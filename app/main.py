from fastapi import FastAPI,WebSocket,WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uuid

app = FastAPI()


origins = [
    "http://localhost:8011/"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

username = str(uuid.uuid4())

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        Send From Client: <ul id='input'>
        Receive From Server:<ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://0.0.0.0:8011/ws/{username}");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""

import time
import asyncio
from typing import List

@app.get("/")
async def get():
    return HTMLResponse(html)


# class ConnectionManager:
#     def __init__(self):
#         self.active_connections : set[WebSocket] = set()

#     async def connect(self,websocket:WebSocket):
#         await websocket.accept()
#         self.active_connections.add(websocket)
    
#     def disconnect(self,websocket:WebSocket):
#         self.active_connections.discard(websocket)
    
#     async def broadcast(self, message:str):
#         for connection in self.active_connections.copy():
#             try:
#                 await connection.send_text(message)
            
#             except Exception as e:
#                 print(f"Error sending to client: {e}")




# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await manager.connect(websocket)
#     try:
#         while True:
#             data = await websocket.receive_text()  # waits for any message to start the sequence
#             print(f"Received from client: {data}")
#             for i in range(1, 10):
#                 print(data)
#                 await asyncio.sleep(1)  # correctly await for non-blocking sleep
#                 await manager.broadcast(f"{i}")
#     except WebSocketDisconnect:
#         manager.disconnect(websocket)
#         print("WebSocket disconnected")

class ConnectionManager:
    def __init__(self):
        self.active_connections : List[WebSocket] = []
        self.usernames : dict[WebSocket,str] = {}
        print(self.active_connections,self.usernames)

    async def connect(self,websocket:WebSocket, username:str):
        await websocket.accept()
        print(websocket)
        self.active_connections.append(websocket)
        self.usernames[websocket] = username
        await self.broadcast("🔵 {username} joined the chat.")
    
    def disconnect(self,websocket:WebSocket):
        username = self.usernames.get(websocket, "Unknown")
        self.active_connections.remove(websocket)
        del self.usernames[websocket]
        return username

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()



@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket,username:str):
    await manager.connect(websocket,username)
    try:
        while True:
            data = await websocket.receive_text()  # waits for any message to start the sequence
            await manager.broadcast(f"{username}: {data}")
    except WebSocketDisconnect:
        disconnected_user = manager.disconnect(websocket)
        await manager.broadcast(f"🔴 {disconnected_user} left the chat.")