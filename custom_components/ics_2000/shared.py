"""Platform for ICS-2000 integration."""

from __future__ import annotations

import enum
from typing import Any

from ics_2000.hub import Hub
from ics_2000.exceptions import InvalidAuthException
from ics_2000.entities import (
    dim_device,
    switch_device,
)
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.components.switch import SwitchEntity
from homeassistant.components.light.const import ColorMode
from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    LightEntity,
)
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, CONF_IP_ADDRESS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from custom_components.ics_2000.const import DOMAIN


# class Type(enum.Enum):
#     Light = "light"
#     Switch = "switch"


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
    config_type: Type | None = None,
) -> None:
    """Set up the Awesome Light platform."""
    # Assign configuration variables.
    # The configuration check takes care they are present.
    username: str = config[CONF_USERNAME]
    password: str = config[CONF_PASSWORD]
    local_address: str | None = config.get(CONF_IP_ADDRESS)

    # Setup connection with devices/cloud
    hub = Hub(username, password)
    hub.local_address = local_address
    hub.login()
    hub.get_devices()

    # # Verify that passed in configuration works
    # if not hub.is_valid_login():
    #     _LOGGER.error("Could not connect to AwesomeLight hub")
    #     return

    # Add devices
    devices = []
    for enitity in hub.devices:
        if type(enitity) is dim_device.DimDevice and config_type == Type.Light:
            devices.append(DimmableLight(enitity))
        if type(enitity) is switch_device.SwitchDevice and config_type == Type.Switch:
            devices.append(Switch(enitity))
    add_entities(devices)
