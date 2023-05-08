from moviestarplanet._api import request
from typing import Optional
from pyamf import remoting
import aiohttp
from moviestarplanet._utils import authorization, histogram, ticketMap
from moviestarplanet._class import amfResult, amfDescription, loginResult, autographResult
import asyncio
import hashlib, binascii
from pyamf import ASObject
from moviestarplanet import mspsocket
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
        self.websocket = mspsocket.MspSocketUser()

    async def send_command_async(self, server: str, method: str, args: dict, proxy: Optional[str]=None):
        '''
           >>> Send a command to MovieStarPlanet.
               ~ Example : await send_command_async('fr', 'MovieStarPlanet.WebService.UserSession.AMFUserSessionService.GetActorIdFromName', ['Username'])
        '''
        amf = await request.post_async(
            session=self._session,
            server=server,
            method=method, 
            arguments=args,
            amfCollectionHeaders=remoting.HeaderCollection(
                {
                    ("sessionID", False, histogram.GenerateHistogram()),
                    ("id", False, authorization.CalculateChecksum(args))
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


    async def login_async(self, username: str, password: str, server: str, use_socket: Optional[bool]=True, proxy: Optional[str]=None):
        '''Log in to MovieStarPlanet'''
        async def send_login_command():
            return await self.send_command_async(
                server,
                'MovieStarPlanet.WebService.User.AMFUserServiceWeb.Login',
                [ username, password, [], None, None, "MSP1-Standalone:XXXXXX" ],
                proxy=proxy
            )

        amf = await asyncio.ensure_future(send_login_command())

        if amf.description == amfDescription.Set.OK:
            if amf.content['loginStatus']['status'] == "InvalidCredentials":
                return loginResult.Result('InvalidCredentials', 0, 0, 0, 0, None, None, None)

            if amf.content['loginStatus']['status'] == 'ERROR':
                return loginResult.Result('ERROR', 0, 0, 0, 0, None, None, None)

            if (amf.content['loginStatus']['status'] == 'Success') or  (amf.content['loginStatus']['status'] == 'ThirdPartyCreated'):
                self.ticket = amf.content['loginStatus']['ticket']
                self.actor_id = amf.content['loginStatus']['actor']['ActorId']
                self.access_token = amf.content['loginStatus']['nebulaLoginStatus']['accessToken']
                self.profile_id =  amf.content['loginStatus']['nebulaLoginStatus']['profileId']
                self.server = server

                if use_socket:
                    await self.websocket.connect(server)
                    await self.websocket.send_authentication(server, amf.content['loginStatus']['nebulaLoginStatus']['accessToken'],amf.content['loginStatus']['nebulaLoginStatus']['profileId'])
                    self.socket_connection = True

                return loginResult.Result(
                    "Success",
                    amf.content['loginStatus']['actor']['ActorId'], 
                    amf.content['loginStatus']['actor']['Money'], 
                    amf.content['loginStatus']['actor']['Fame'], 
                    amf.content['loginStatus']['actor']['Diamonds'], 
                    amf.content['loginStatus']['ticket'], 
                    amf.content['loginStatus']['nebulaLoginStatus']['profileId'],
                    amf.content['loginStatus']['nebulaLoginStatus']['accessToken']
                )
            return loginResult.Result('ERROR', 0, 0, 0, 0, None, None, None)


    async def get_actorid_from_name_async(self, username: str, server: str) -> int:
        '''Get the ActorId of someone with the username'''
        async def send_actorid_command():
            return await self.send_command_async(server, "MovieStarPlanet.WebService.UserSession.AMFUserSessionService.GetActorIdFromName", [username])

        amf = await asyncio.ensure_future(send_actorid_command())
        return amf.content

    async def give_autograph_async(self, actor_id: int, use_socket: Optional[bool]=True, ticket: Optional[str]=None, proxy: Optional[str]=None):
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
            
        amf = await asyncio.ensure_future(send_autograph_command())
        print(amf)
        return autographResult.Result(amf.content['Fame'], amf.content['Timestamp'])


    async def map_async(self, tasks):
        return await asyncio.gather(*tasks)
