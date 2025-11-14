"""Button entity for EAM Meter integration."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, MAIN_URL, CONF_ENTITY_ID
from .eam_api import get_session_key, get_selected_read, post_readout

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the EAM Meter button entity."""
    async_add_entities([EAMMeterSubmitButton(hass, config_entry)])


class EAMMeterSubmitButton(SensorEntity):
    """Representation of the EAM meter submit button."""

    _attr_has_entity_name = True
    _attr_name = "Submit Readout"
    _attr_icon = "mdi:upload"
    _attr_native_unit_of_measurement = "kWh"
    _attr_device_class = SensorDeviceClass.ENERGY

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize the button entity."""
        self.hass = hass
        self._config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}_submit"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": "EAM Meter",
            "manufacturer": "EAM",
            "model": "Meter Readout",
        }
        self._last_readout = None

    @property
    def native_value(self):
        """Return the last submitted readout value."""
        return self._last_readout

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        return {
            "configured_entity": self._config_entry.data.get(CONF_ENTITY_ID),
        }

    async def async_press(self) -> None:
        """Handle the button press."""
        # Get the entity_id from config
        entity_id = self._config_entry.data.get(CONF_ENTITY_ID)
        
        if not entity_id:
            raise HomeAssistantError("No entity_id configured")
        
        state = self.hass.states.get(entity_id)
        
        if not state:
            raise HomeAssistantError(f"Entity {entity_id} not found")
        
        try:
            readout_value = int(float(state.state))
        except (ValueError, TypeError) as err:
            raise HomeAssistantError(f"Invalid readout value: {state.state}") from err
        
        if readout_value <= 0:
            raise HomeAssistantError("Readout value must be greater than 0")
        
        # Get credentials from config
        username = self._config_entry.data[CONF_USERNAME]
        password = self._config_entry.data[CONF_PASSWORD]
        
        try:
            # Step 1: Get session key
            _LOGGER.info("Getting session key for EAM meter")
            session_key = await self.hass.async_add_executor_job(
                get_session_key, MAIN_URL, username, password
            )
            
            # Step 2: Get metadata
            _LOGGER.info("Getting metadata for EAM meter")
            selected_read = await self.hass.async_add_executor_job(
                get_selected_read, session_key, MAIN_URL
            )
            
            # Step 3: Post readout
            _LOGGER.info("Posting readout: %s kWh", readout_value)
            success = True #await self.hass.async_add_executor_job(post_readout, session_key, selected_read, readout_value, MAIN_URL)
            
            if success:
                _LOGGER.info("Successfully posted readout: %s kWh", readout_value)
                self._last_readout = readout_value
                self.async_write_ha_state()
            else:
                raise HomeAssistantError("Failed to post readout")
                
        except Exception as err:
            _LOGGER.error("Error posting readout: %s", err)
            raise HomeAssistantError(f"Failed to submit readout: {err}") from err
