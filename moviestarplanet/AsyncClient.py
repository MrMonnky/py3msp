from typing import Optional
from pyamf import remoting
import aiohttp
from authorization import CalculateChecksum
from histogram import GenerateHistogram
from ticketMap import check
from amfResult import Result as amfResult
from amfDescription import Description as amfDescription
from loginResult import Result as loginResult
from autographResult import Result as autographResult
import asyncio
import hashlib
import binascii
from pyamf import ASObject
from mspsocket import MspSocketUser
import random

class AsyncClient():
    def __init__(self):
        self._session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=11111110, ttl_dns_cache=11111110))
        self.ticket: str = None
        self.profile_id: str = None
        self.server = None
        self.access_token: str = None
        self.actor_id = None
        self.socket_connection: bool = False
        self.websocket = MspSocketUser()

    async def send_command_async(self, server: str, command: dict, proxy: Optional[str] = None):
        '''
           >>> Send a command to MovieStarPlanet.
               ~ Example: await send_command_async('fr', {'serviceName': 'MovieStarPlanet.WebService.UserSession.AMFUserSessionService.GetActorIdFromName', 'data': ['Username']})
        '''
        amf = await request.post_async(
            session=self._session,
            server=server,
            method=command["serviceName"],
            arguments=command["data"],
            amfCollectionHeaders=remoting.HeaderCollection(
                {
                    ("sessionID", False, histogram.GenerateHistogram()),
                    ("id", False, authorization.CalculateChecksum(command["data"]))
                }),
            proxy=proxy
        )
        return amf

    def authorize_user(self, ticket: str):
        """
         Updating ticket markingId
        """
        marking_id = int(random.uniform(0.0, 0.1) * 1000) + 1
        loc1bytes = str(marking_id).encode('utf-8')
        loc5 = hashlib.md5(loc1bytes).hexdigest()
        loc6 = binascii.hexlify(loc1bytes).decode()
        return ASObject({"Ticket": ticket + loc5 + loc6, "anyAttribute": None})

    async def login_async(self, username: str, password: str, server: str, use_socket: Optional[bool] = True, proxy: Optional[str] = None):
        # Funktion zum Senden des Login-Befehls
        async def send_login_command():
            command = {
                "serviceName": "MovieStarPlanet.WebService.User.AMFUserServiceWeb.Login",
                "data": [username, password, [], None, None, "MSP1-Standalone:XXXXXX"]
            }
            return await self.send_command_async(server, command, proxy=proxy)

        # Senden des Login-Befehls und Empfang der Antwort
        amf_response = await send_login_command()

        # Überprüfen der Antwort und Verarbeiten der Ergebnisse
        if amf_response.description == amfDescription.Set.OK:
            login_status = amf_response.content.get("loginStatus", {})

            # Überprüfen, ob die Anmeldedaten ungültig sind
            if login_status.get("status") == "InvalidCredentials":
                return loginResult.Result('InvalidCredentials', 0, 0, 0, 0, None, None, None)

            # Überprüfen, ob ein allgemeiner Fehler aufgetreten ist
            if login_status.get("status") == "ERROR":
                return loginResult.Result('ERROR', 0, 0, 0, 0, None, None, None)

            # Überprüfen, ob die Anmeldung erfolgreich war
            if login_status.get("status") in ["Success", "ThirdPartyCreated"]:
                self.ticket = login_status.get("ticket")
                self.actor_id = login_status["actor"].get("ActorId")
                nebula_login_status = login_status.get("nebulaLoginStatus", {})
                self.access_token = nebula_login_status.get("accessToken")
                self.profile_id = nebula_login_status.get("profileId")
                self.server = server

                # Verbindung zum WebSocket-Server herstellen und Authentifizierung senden
                if use_socket:
                    await self.websocket.connect(server)
                    await self.websocket.send_authentication(server, self.access_token, self.profile_id)
                    self.socket_connection = True

                # Ergebnis der erfolgreichen Anmeldung zurückgeben
                return loginResult.Result(
                    "Success",
                    self.actor_id,
                    login_status["actor"].get("Money", 0),
                    login_status["actor"].get("Fame", 0),
                    login_status["actor"].get("Diamonds", 0),
                    self.ticket,
                    self.profile_id,
                    self.access_token
                )

        # Wenn keines der vorherigen Ergebnisse erfüllt ist, wird ein Fehler zurückgegeben
        return loginResult.Result('ERROR', 0, 0, 0, 0, None, None, None)

    async def get_actorid_from_name_async(self, username: str, server: str) -> int:
        '''Get the ActorId of someone with the username'''
        async def send_actorid_command():
            command = {
                "serviceName": "MovieStarPlanet.WebService.UserSession.AMFUserSessionService.GetActorIdFromName",
                "data": [username]
            }
            return await self.send_command_async(server, command)

        amf_response = await send_actorid_command()
        return amf_response.content.get("ActorId", 0)

    async def give_autograph_async(self, actor_id: int, use_socket: Optional[bool] = True, ticket: Optional[str] = None, proxy: Optional[str] = None):
        '''
           Give someone an autograph.
        '''
        async def send_autograph_command():
            actorid = 0
            w_ticket = None
            ticket: str = None
            if ticket != None:
                ticket = ticket
                actorid = ticket.split(',')[1]

            else:
                ticket = self.ticket
                actorid = self.actor_id

            if ticketMap.check(ticket):
                w_ticket = ticket.split('|')[0]

                if use_socket:
                    await self.websocket.connect(self.server)
                    await self.websocket.send_authentication(ticket.split(',')[0], ticket.split(',')[6], ticket.split(',')[5])
            else:
                if (use_socket == False) and (self.socket_connection == True):
                    await self.websocket.connect(self.server)
                    await self.websocket.send_authentication(self.server, self.access_token, self.profile_id)

            return await self.send_command_async(self.server, "MovieStarPlanet.WebService.AMFActorService.GiveAutographAndCalculateTimestamp", [
                self.authorize_user(ticket),
                actorid,
                actor_id
            ])

        amf_response = await send_autograph_command()
        print(amf_response)
        return autographResult.Result(amf_response.content.get('Fame', 0), amf_response.content.get('Timestamp'))

    async def map_async(self, tasks):
        return await asyncio.gather(*tasks)
