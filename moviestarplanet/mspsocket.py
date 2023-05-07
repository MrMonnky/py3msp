import asyncio
import json
import base64
import time, aiohttp
import requests
import websockets

class MspSocketUser:
    def __init__(self):
        """
        Initializes a new instance of the MspSocketUser class.
        """
        self.web_socket_path = None
        self.websocket = None
        self.connected = False
        self.session = aiohttp.ClientSession()
        
        
    async def connect(self, server):
        """
        Connects to the WebSocket server.
        """
        self.web_socket_path = await self.get_web_socket_url(server)
        self.websocket = await websockets.connect(f"ws://{self.web_socket_path.replace('-', '.')}:{10843}/{self.web_socket_path.replace('.', '-')}/?transport=websocket")
        self.connected = True
        ##asyncio.create_task(self.send_ping())

    async def send_ping(self):
        """
        Sends a ping message to the server every 5 seconds.
        """
        ping_id = 0
        await asyncio.sleep(5)
        ping_message = {
                "pingId": ping_id,
                "messageType": 500
            }
        await self.websocket.send(f"42[\"500\",{json.dumps(ping_message)}]")
        ping_id += 1
    
    async def wait_is_connected(self):
        """
        Waits until the WebSocket connection is established.
        """
        while self.websocket is None or not self.websocket.open:
            await asyncio.sleep(0.1)
            
    async def on_message(self, message):
        """
        Handles incoming WebSocket messages.

        :param message: The message received from the server.
        """
        if message.startswith("42"):
            message_parse = message[2:]
            message_parsed = json.loads(message_parse)
            if message_parsed[1]["messageType"] == 11:
                if message_parsed[1]["messageContent"]["success"]:
                    if hasattr(self, "on_connected"):
                        self.on_connected()
    
    async def send_authentication(self, server, access_token, profile_id):
        await self.wait_is_connected()
        auth_message = {
            "messageContent": {
                "country": str(server).upper(),
                "version": 1,
                "access_token": access_token,
                "applicationId": "APPLICATION_WEB",
                "username": profile_id
            },
            "senderProfileId": None,
            "messageType": 10
        }
        await self.websocket.send(f"42[\"10\",{json.dumps(auth_message)}]")

    async def get_web_socket_url(self, server):
        """
          Gets the WebSocket URL for the specified server.

          :param server: The server to connect to (either "US" or "non-US").
          :return: The WebSocket URL for the specified server.
        """
        url = "https://presence.mspapis.com/getServer"
        if server == "US":
            url = "https://presence-us.mspapis.com/getServer"
        async with self.session.get(url) as response:
            return await response.text()
       
