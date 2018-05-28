"""
Support for package info from 17track.net

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/sensor.seventeen_track/
"""
from logging import getLogger

from homeassistant.components.seventeentrack.const import (
    CONF_DATA_OBJ, CONF_TRACKING_NUMBER, DATA_EVENTS, DATA_SUBSCRIBERS,
    DATA_TOPIC_NEW, DATA_TOPIC_UPDATE, DEFAULT_ATTRIBUTION, DOMAIN)
from homeassistant.const import ATTR_ATTRIBUTION, ATTR_LOCATION
from homeassistant.core import callback
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.dispatcher import async_dispatcher_connect

DEPENDENCIES = ['seventeentrack']
_LOGGER = getLogger(__name__)

ATTR_DESTINATION = 'destination_country'
ATTR_INFO = 'info'
ATTR_ORIGIN = 'origin_country'


async def setup_platform(hass, config, add_devices, discovery_info=None):
    """Don't instantiate platform via config."""
    pass


async def async_setup_entry(hass, config_entry, async_add_devices):
    """Set up the deCONZ sensors."""

    @callback
    def async_add_sensor(entry):
        """Add a new 17track.net sensor."""
        async_add_devices([
            PackageSensor(hass.data[DOMAIN][CONF_DATA_OBJ],
                          entry.data[CONF_TRACKING_NUMBER])
        ], True)

    hass.data[DOMAIN][DATA_SUBSCRIBERS].append(
        async_dispatcher_connect(hass, DATA_TOPIC_NEW, async_add_sensor))

    async_add_sensor(config_entry)


class PackageSensor(Entity):
    """Define a sensor for a 17track.net package."""

    def __init__(self, data, tracking_number):
        """Initialize."""
        self._attrs = {ATTR_ATTRIBUTION: DEFAULT_ATTRIBUTION}
        self._seventeentrack = data
        self._state = None
        self._tracking_number = tracking_number

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        return self._attrs

    @property
    def icon(self):
        """Return the icon."""
        return 'mdi:package'

    @property
    def name(self):
        """Return the name."""
        return self._tracking_number

    @property
    def state(self):
        """Return the state."""
        return self._state

    @property
    def unique_id(self):
        """Return a unique, HASS-friendly identifier for this entity."""
        return self._tracking_number

    @callback
    async def async_added_to_hass(self):
        """Register callbacks."""

        def update_data():
            """Update the state."""
            self.async_schedule_update_ha_state(True)

        self.hass.data[DOMAIN][DATA_EVENTS].append(
            async_dispatcher_connect(self.hass, DATA_TOPIC_UPDATE,
                                     update_data))

    def update(self):
        """Update the sensor's state data."""
        # package = self._seventeentrack.packages[self._tracking_number]
        [package] = [
            p for p in self._seventeentrack.packages
            if p.tracking_number == self._tracking_number
        ]

        self._state = package.status
        self._attrs.update({
            ATTR_DESTINATION: package.destination_country,
            ATTR_INFO: package.info_text,
            ATTR_LOCATION: package.location,
            ATTR_ORIGIN: package.origin_country,
        })
