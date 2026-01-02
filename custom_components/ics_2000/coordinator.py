"""Example integration using DataUpdateCoordinator."""

from datetime import timedelta
import logging

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from ics_2000.hub import Hub

_LOGGER = logging.getLogger(__name__)


class ICS200Coordinator(DataUpdateCoordinator):
    """Coordinator for updating data to and from klikaanklikuit."""

    def __init__(self, hass, config_entry, hub):
        """Initialize the klikaanklikuit coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="KlikAanKlikUit",
            config_entry=config_entry,
            update_interval=timedelta(seconds=2),
            always_update=True,
        )
        self.hub: Hub = hub

    async def _async_update_data(self):
        return await self.hass.async_add_executor_job(self.hub.get_all_device_statuses)
