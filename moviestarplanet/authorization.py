import hashlib
import binascii
import random
import base64
from typing import List, Union
from datetime import date, datetime
from urllib.parse import urlparse
import pyamf
from pyamf import remoting, ASObject, TypedObject, AMF3
from pyamf import amf3
import io
from typing import Union, List, Optional

def CalculateChecksum(arguments: Union[int, str, bool, bytes, List[Union[int, str, bool, bytes]], dict, date, datetime, ASObject, TypedObject]) -> str:
    '''
       This calculate given objects to an hash to authorize requests.
    '''

    checked_objects: dict = {}
    no_ticket_value: str = "v1n3g4r"
    salt: str = "$CuaS44qoi0Mp2qp"

    def from_object(obj: Union[None, int, str, bool, amf3.ByteArray, datetime.date, datetime, List[Union[int, str, bool, bytes]], dict, ASObject, TypedObject]) -> str:
        if obj is None: return ""

        if isinstance(obj, (int, str, bool)):
            return str(obj)

        if isinstance(obj, amf3.ByteArray):
            return from_byte_array(obj)

        if isinstance(obj, (date, datetime)):
            return str(obj.year) + str(obj.month - 1) + str(obj.day)

        if isinstance(obj, (list, dict)) and "Ticket" not in obj:
            return from_array(obj)

        return ""

    def from_byte_array(bytes: Union[io.BytesIO, amf3.ByteArray]) -> str:
        if len(bytes) <= 20:
            return bytes.getvalue().hex()

        num: int = len(bytes) // 20
        array = bytearray(20)
        for i in range(20):
            bytes.seek(num * i)
            array[i] = bytes.read(1)[0]

        return array.hex()

    def from_array(arr):
        result = ""
        for item in arr:
            if isinstance(item, (ASObject, TypedObject)):
                result += from_object(item)
            else:
                result += from_object_inner(item)
        return result

    def get_ticket_value(arr):
        for obj in arr:
            if isinstance(obj, ASObject) and "Ticket" in obj:
                ticket_str = obj["Ticket"]
                if ',' in ticket_str:
                    return ticket_str.split(',')[5][:5]
        return no_ticket_value

    def from_object_inner(obj):
        result = ""
        if isinstance(obj, dict):
            for key in sorted(obj.keys()):
                if key not in checked_objects:
                    result += from_object(obj[key])
                    checked_objects[key] = True
        else:
            result += from_object(obj)
        return result

    result_str = from_object_inner(arguments) + get_ticket_value(arguments) + salt
    return hashlib.sha1(result_str.encode()).hexdigest()