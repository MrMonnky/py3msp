import base64, random

def GenerateHistogram() -> str | None:
        '''
            Generate a random MovieStarPlanet sessionID.
        '''
        return base64.b64encode(''.join(f'{random.randint(0, 15):x}' for _ in range(48))[:46].encode()).decode()
