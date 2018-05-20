"""Define data and entity objects for 17track packages."""
from datetime import timedelta

from homeassistant.const import ATTR_ATTRIBUTION, ATTR_LOCATION
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

from .const import LOGGER

ATTR_DESTINATION = 'destination_country'
ATTR_INFO = 'info'
ATTR_ORIGIN = 'origin_country'

DEFAULT_ATTRIBUTION = 'Data provided by 17track.net'
DEFAULT_SCAN_INTERVAL = timedelta(seconds=60 * 60 * 6)


class PackageSensor(Entity):
    """Define a sensor for a 17track.net package."""

    def __init__(self, data, tracking_number):
        """Initialize."""
        self._attrs = {ATTR_ATTRIBUTION: DEFAULT_ATTRIBUTION}
        self._data = data
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

    def update(self):
        """Update the sensor's state data."""
        self._data.update()

        package = self._data.packages[self._tracking_number]

        if not package.tracking_number:
            LOGGER.warning("Can't find data for package; verify on website")
            return

        self._attrs.update({
            ATTR_DESTINATION: package.destination_country,
            ATTR_INFO: package.info,
            ATTR_LOCATION: package.location,
            ATTR_ORIGIN: package.origin_country,
        })
        self._state = package.status


class SeventeenTrackData(object):
    """Define a data object to retrieve data from 17track.net."""

    def __init__(self, client):
        """Initialize."""
        self._client = client
        self.package_data = {}
        self.tracking_numbers = []

    @Throttle(DEFAULT_SCAN_INTERVAL)
    def update(self):
        """Update the data."""
        data = self._client.track(*self.tracking_numbers)

        LOGGER.debug('New data received: %s', data)

        self.package_data = data
