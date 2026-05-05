"""Platform for ICS-2000 blinds integration."""

from __future__ import annotations

import logging

from .coordinator import ICS200Coordinator
from ics_2000.entities import blind_device

from homeassistant.components.cover import (
    CoverEntity,
    CoverEntityFeature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import HubConfigEntry
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: HubConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up blinds."""
    async_add_entities(
        [
            WindowBlind(entry.runtime_data, entity)
            for entity in entry.runtime_data.hub.devices
            if type(entity) is blind_device.BlindDevice
        ]
    )


class WindowBlind(CoordinatorEntity[ICS200Coordinator], CoverEntity):
    """Representation of a stateless window blind."""

    _attr_has_entity_name = True
    _attr_name = None

    _attr_assumed_state = True

    _attr_supported_features = (
        CoverEntityFeature.OPEN
        | CoverEntityFeature.CLOSE
        | CoverEntityFeature.STOP
    )

    def __init__(
        self,
        coordinator: ICS200Coordinator,
        blind: blind_device.BlindDevice,
    ) -> None:
        """Initialize blind."""
        super().__init__(coordinator, context=str(blind.entity_id))

        self._blind = blind

        self._attr_unique_id = str(blind.entity_id)
        self._attr_is_closed = None

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, blind.device_data.id)},
            name=str(blind.name),
            model=blind.device_config.model_name,
            model_id=str(blind.device_data.device),
            sw_version=str(
                blind.device_data.data.get("module", {}).get("version", "")
            ),
        )

    @property
    def icon(self) -> str:
        """Return icon."""
        return "mdi:blinds"

    async def async_open_cover(self, **kwargs) -> None:
        """Open blind."""
        await self.hass.async_add_executor_job(self._blind.open)

    async def async_close_cover(self, **kwargs) -> None:
        """Close blind."""
        await self.hass.async_add_executor_job(self._blind.close)

    async def async_stop_cover(self, **kwargs) -> None:
        """Stop blind."""
        await self.hass.async_add_executor_job(self._blind.stop)