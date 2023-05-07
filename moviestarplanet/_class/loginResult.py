from moviestarplanet._class import amfDescription
from dataclasses import dataclass

@dataclass
class Result:
    Status: str
    ActorId: int
    StarCoins: int
    Fame: int
    Diamonds: int
    Ticket: str
    ProfileId: str
    AccessToken: str
