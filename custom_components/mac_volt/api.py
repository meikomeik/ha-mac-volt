"""API Placeholder.

You should create your api seperately and have it hosted on PYPI.  This is included here for the sole purpose
of making this example code executable.
"""

from dataclasses import dataclass
from enum import StrEnum

import asyncio
import aiohttp
import datetime
import logging

from homeassistant.config_entries import ConfigEntry

from random import choice, randrange

_LOGGER = logging.getLogger(__name__)


class DeviceType(StrEnum):
    """Device types."""

    TEMP_SENSOR = "temp_sensor"
    DOOR_SENSOR = "door_sensor"
    OTHER = "other"


DEVICES = [
    {"id": 1, "type": DeviceType.TEMP_SENSOR},
    {"id": 2, "type": DeviceType.TEMP_SENSOR},
    {"id": 3, "type": DeviceType.TEMP_SENSOR},
    {"id": 4, "type": DeviceType.TEMP_SENSOR},
    {"id": 1, "type": DeviceType.DOOR_SENSOR},
    {"id": 2, "type": DeviceType.DOOR_SENSOR},
    {"id": 3, "type": DeviceType.DOOR_SENSOR},
    {"id": 4, "type": DeviceType.DOOR_SENSOR},
]


@dataclass
class Device:
    """API device."""

    device_id: int
    device_unique_id: str
    device_type: DeviceType
    name: str
    state: int | bool


class API:
    """Class for example API."""

    #def __init__(self, host: str, username: str, password: str, config_entry: ConfigEntry) -> None:
    def __init__(self, username: str, password: str) -> None:
        """Initialise."""
        self.host = "https://monitor.macvolt.de/api"
        self.username = username
        self.password = password
        self.connected: bool = False
        self.token = ''
        self.refresh_token = ''

    @property
    def controller_name(self) -> str:
        """Return the name of the controller."""
        return self.username.replace(".", "_")

    def _get_headers(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:146.0) Gecko/20100101 Firefox/146.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Content-Type': 'application/json',
            'platform': 'AK9D8H',
            'System': 'macvolt',
            'language': 'en-US',
            'operationDate': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'Origin': 'https://monitor.macvolt.de',
            'Connection': 'keep-alive',
            'Referer': 'https://monitor.macvolt.de/login',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Priority': 'u=0',
            'TE': 'trailers',
        }
        if self.token:
            headers['Authorization'] = self.token
        return headers

    async def connect(self) -> bool:
        """Connect to api."""
        _LOGGER.info("MACVOLT: connect!")

        PATH_LOGIN = "/usercenter/cloud/user/login"

        login_url = f'{self.host}{PATH_LOGIN}'
        post_data = f'{{"username": "{self.username}", "password": "{self.password}"}}'
        headers = self._get_headers()
        _LOGGER.info(f"MACVOLT: headers={headers}!")

        async with aiohttp.ClientSession() as session:
            response = await session.post(url=login_url,
                                    data=post_data,
                                    headers=headers)
            result = response.json()
            if result['code'] == 200:
                _LOGGER.info("MACVOLT: Login successful!")
                self.connected = True
                self.token = result['data']['token']
                self.refresh_token = result['data']['refreshToken']
                return True
        raise APIAuthError("Error connecting to api. Invalid username or password.")

    def disconnect(self) -> bool:
        """Disconnect from api."""
        self.connected = False
        return True

    async def get_devices(self) -> list[Device]:
        """Get devices on api."""
        _LOGGER.info("MACVOLT: GET_DEVICES")

        PATH_SYSTEM_SN = "/stable/home/getCustomMenuEssList"

        path_system_sn = f'{self.host}{PATH_SYSTEM_SN}'
        headers = self._get_headers()

        async with aiohttp.ClientSession() as session:
            response = await session.get(url=path_system_sn, headers=headers)
            result = response.json()
            if result['code'] == 200:
                _LOGGER.info("MACVOLT: GET_SN successful!")
                self.system = []
                for item in result['data']:
                    self.system.append(item['SystemSn'])
                _LOGGER.info("MACVOLT: SN {self.system}!")

    def get_device_unique_id(self, device_id: str, device_type: DeviceType) -> str:
        """Return a unique device id."""
        if device_type == DeviceType.DOOR_SENSOR:
            return f"{self.controller_name}_D{device_id}"
        if device_type == DeviceType.TEMP_SENSOR:
            return f"{self.controller_name}_T{device_id}"
        return f"{self.controller_name}_Z{device_id}"

    def get_device_name(self, device_id: str, device_type: DeviceType) -> str:
        """Return the device name."""
        if device_type == DeviceType.DOOR_SENSOR:
            return f"DoorSensor{device_id}"
        if device_type == DeviceType.TEMP_SENSOR:
            return f"TempSensor{device_id}"
        return f"OtherSensor{device_id}"

    def get_device_value(self, device_id: str, device_type: DeviceType) -> int | bool:
        """Get device random value."""
        if device_type == DeviceType.DOOR_SENSOR:
            return choice([True, False])
        if device_type == DeviceType.TEMP_SENSOR:
            return randrange(15, 28)
        return randrange(1, 10)


class APIAuthError(Exception):
    """Exception class for auth error."""


class APIConnectionError(Exception):
    """Exception class for connection error."""
