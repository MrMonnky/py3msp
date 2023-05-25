import aiohttp
from typing import Union, Optional
import pyamf
from pyamf import remoting
from moviestarplanet._utils import histogram, authorization
from moviestarplanet._class import amfResult, amfDescription
from moviestarplanet._api import proxyBuilder

async def post_async(session: aiohttp.ClientSession, server: str, method: str, arguments: dict, headers: Optional[dict]={'Content-Type': 'application/x-amf', 'Referer': 'app:/cache/t1.bin/[[DYNAMIC]]/2'}, 
                      amfCollectionHeaders: Optional[pyamf.remoting.HeaderCollection]=None, proxy: Optional[str]=None):
    '''Sends AMF3 request.'''

    proxy = proxyBuilder.fix(proxy)
    request = remoting.Request(target=method, body=arguments)
    event = remoting.Envelope(pyamf.AMF3)
    
    event.headers = amfCollectionHeaders
    event['/1'] = request
    encoded_req = remoting.encode(event).getvalue()

    async with session.post(f'http://api.moviestarplanet.{server}/Gateway.aspx?method={method}', data=encoded_req, headers=headers, proxy=proxy) as response:
        status = response.status
        response = await response.read()
    
        if str(status) == "200":
            try:
                return amfResult.Result(status, remoting.decode(response)["/1"].body, amfDescription.Set.OK)
            except:
                return amfResult.Result(status, None, amfDescription.Set.ERROR)
            

        if str(status) == "403":
            return amfResult.Result(status, None, amfDescription.Set.FORBIDDEN)
        
        if str(status) == "500":
            return amfResult.Result(status, None, amfDescription.Set.INTERNAL_SERVER_ERROR)
        
        if str(status) == "400":
            return amfResult.Result(status, None, amfDescription.Set.BAD_REQUEST)

        if (str(status) == "502") or (str(status) == "503"):
            return amfResult.Result(status, None, amfDescription.Set.PROXY_ERROR)

