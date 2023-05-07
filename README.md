# py3msp
A fast python3 MovieStarPlanet1 client with ticket gestion with proxy and bytearray support

usage:

```py

import moviestarplanet, asyncio

async def main():
    msp = moviestarplanet.AsyncClient()
    
    login = await msp.login_async(username, password, password, use_socket=True)
    if login.Status == 'Success':
        autographResult = await msp.give_autograph_async(actor_id)
        print(autographResult)
    
```
