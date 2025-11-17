"""Sensor entity for EAM Meter integration."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD, UnitOfEnergy
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN, MAIN_URL
from .eam_api import get_session_key, get_last_readout

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(hours=6)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the EAM Meter sensor entity."""
    username = config_entry.data[CONF_USERNAME]
    password = config_entry.data[CONF_PASSWORD]

    async def async_update_data():
        """Fetch data from EAM portal."""
        try:
            session_key = await hass.async_add_executor_job(
                get_session_key, MAIN_URL, username, password
            )
            value, date_str = await hass.async_add_executor_job(
                get_last_readout, session_key, MAIN_URL
            )
            return {
                "value": value,
                "date": date_str
            }
        except Exception as err:
            raise UpdateFailed(f"Error communicating with EAM portal: {err}") from err

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="EAM Meter",
        update_method=async_update_data,
        update_interval=SCAN_INTERVAL,
    )

    await coordinator.async_config_entry_first_refresh()

    # Store coordinator in hass.data for button access
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault(config_entry.entry_id, {})
    hass.data[DOMAIN][config_entry.entry_id]["coordinator"] = coordinator

    async_add_entities([EAMLastReadoutSensor(coordinator, config_entry)])


class EAMLastReadoutSensor(CoordinatorEntity, SensorEntity):
    """Representation of the EAM meter last readout sensor."""

    _attr_has_entity_name = True
    _attr_name = "Last Readout"
    _attr_icon = "mdi:counter"
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_suggested_display_precision = 0

    def __init__(self, coordinator: DataUpdateCoordinator, config_entry: ConfigEntry) -> None:
        """Initialize the sensor entity."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}_last_readout"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": "EAM Meter",
            "manufacturer": "EAM",
            "model": "Meter Readout",
        }

    @property
    def native_value(self) -> int | None:
        """Return the last submitted readout value."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("value")
    
    @property
    def extra_state_attributes(self) -> dict[str, str] | None:
        """Return additional attributes."""
        if self.coordinator.data is None:
            return None
        return {
            "date": self.coordinator.data.get("date")
        }
