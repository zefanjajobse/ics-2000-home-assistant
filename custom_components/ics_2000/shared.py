"""Platform for ICS-2000 integration."""

from __future__ import annotations

import enum
from typing import Any

from ics_2000.hub import Hub
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


class Type(enum.Enum):
    Light = "light"
    Switch = "switch"


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


class DimmableLight(LightEntity):
    """Representation of an dimmable light."""

    def __init__(self, light: dim_device.DimDevice) -> None:
        """Initialize an dimmable light."""
        self._light = light
        self._name = str(light.name)
        self._state = self._light.get_on_status()
        self._brightness = self._light.get_dim_level()
        self._attr_color_mode = ColorMode.BRIGHTNESS

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._light.device_data.id)},
            name=self.name,
            model=self._light.device_config.model_name,
            model_id=str(self._light.device_data.device),
            sw_version=str(
                self._light.device_data.data.get(
                    "module", {}).get("version", "")
            ),
        )

    @property
    def icon(self) -> str | None:
        """Icon of the entity."""
        return "mdi:lightbulb"

    @property
    def name(self) -> str:
        """Return the display name of this light."""
        return self._name

    @property
    def color_mode(self):
        """Set color mode for this entity."""
        return ColorMode.BRIGHTNESS

    @property
    def supported_color_modes(self):
        """Flag supported color_modes (in an array format)."""
        return [ColorMode.BRIGHTNESS]

    @property
    def brightness(self):
        """Return the brightness of the light.

        This method is optional. Removing it indicates to Home Assistant
        that brightness is not supported for this light.
        """
        return self._brightness

    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        return self._state

    def turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on.

        You can skip the brightness part if your light does not support
        brightness control.
        """
        self._light.dim(kwargs.get(ATTR_BRIGHTNESS, 255), False)
        self._light.turn_on(self._light._hub.local_address is not None)

    def turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        self._light.turn_off(self._light._hub.local_address is not None)

    def update(self) -> None:
        """Fetch new state data for this light.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._state = self._light.get_on_status()
        self._brightness = self._light.get_dim_level()


class Switch(SwitchEntity):
    def __init__(self, switch: switch_device.SwitchDevice) -> None:
        """Initialize an switch."""
        self._switch = switch
        self._name = str(switch.name)
        self._state = self._switch.get_on_status()

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._switch.device_data.id)},
            name=self.name,
            model=self._switch.device_config.model_name,
            model_id=str(self._switch.device_data.device),
            sw_version=str(
                self._switch.device_data.data.get(
                    "module", {}).get("version", "")
            ),
        )

    @property
    def icon(self) -> str | None:
        """Icon of the entity."""
        return "mdi:flash"

    @property
    def name(self) -> str:
        """Return the display name of this switch."""
        return self._name

    @property
    def is_on(self) -> bool | None:
        """Return true if switch is on."""
        return self._state

    def turn_on(self, **kwargs: Any) -> None:
        """Instruct the switch to turn on.

        You can skip the brightness part if your switch does not support
        brightness control.
        """
        self._switch.turn_on(self._switch._hub.local_address is not None)

    def turn_off(self, **kwargs: Any) -> None:
        """Instruct the switch to turn off."""
        self._switch.turn_off(self._switch._hub.local_address is not None)

    def update(self) -> None:
        """Fetch new state data for this switch.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._state = self._switch.get_on_status()
