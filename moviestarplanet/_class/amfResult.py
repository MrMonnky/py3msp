from moviestarplanet._class import amfDescription
from dataclasses import dataclass

@dataclass
class Result:
    status_code: int
    content: dict
    description: amfDescription.Set