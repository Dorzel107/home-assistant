"""
Support for package info from 17track.net

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/sensor.seventeen_track/
"""
from logging import getLogger

from homeassistant.components.seventeentrack.const import (
    CONF_TRACKING_NUMBER, DATA_OBJ, DATA_SUBSCRIBERS, DATA_TOPIC_UPDATE,
    DOMAIN)
from homeassistant.const import ATTR_ATTRIBUTION, ATTR_LOCATION
from homeassistant.core import callback
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.dispatcher import async_dispatcher_connect

DEPENDENCIES = ['seventeentrack']
_LOGGER = getLogger(__name__)

ATTR_DESTINATION = 'destination_country'
ATTR_INFO = 'info'
ATTR_ORIGIN = 'origin_country'

DEFAULT_ATTRIBUTION = 'Data provided by 17track.net'


async def setup_platform(hass, config, add_devices, discovery_info=None):
    """Don't instantiate platform via config."""
    pass


async def async_setup_entry(hass, config_entry, async_add_devices):
    """Set up the 17track.net sensors."""
    seventeentrack = hass.data[DOMAIN][DATA_OBJ]

    if config_entry.data.get(CONF_TRACKING_NUMBER):
        async_add_devices([
            PackageSensor(seventeentrack,
                          config_entry.data[CONF_TRACKING_NUMBER])
        ], True)
    else:
        async_add_devices([
            PackageSensor(seventeentrack, package.tracking_number)
            for package in seventeentrack.account_packages
        ], True)


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

    async def async_added_to_hass(self):
        """Register callbacks."""

        @callback
        def update_data():
            """Update the state."""
            self.async_schedule_update_ha_state(True)

        self.hass.data[DOMAIN][DATA_SUBSCRIBERS][
            self._tracking_number] = async_dispatcher_connect(
                self.hass, DATA_TOPIC_UPDATE, update_data)

    def update(self):
        """Update the sensor's state data."""
        try:
            [package] = [
                p for p in self._seventeentrack.ad_hoc_packages +
                self._seventeentrack.account_packages
                if p.tracking_number == self._tracking_number
            ]
        except ValueError:
            _LOGGER.error('No data for tracking number: %s',
                          self._tracking_number)
            return

        self._state = package.status
        self._attrs.update({
            ATTR_DESTINATION: package.destination_country,
            ATTR_INFO: package.info_text,
            ATTR_LOCATION: package.location,
            ATTR_ORIGIN: package.origin_country,
        })
