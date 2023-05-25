from enum import Enum

class Set(Enum):
    BAD_REQUEST = "Server returned bad request cuz of wrong method used"
    INTERNAL_SERVER_ERROR = "Server is being spammed or sessionID issue"
    PROXY_ERROR = "An error occurred with the proxy"
    ERROR = "An error occurred when parsing response"
    FORBIDDEN = "IP Address is blocked"
    OK = "Response is Okay"
