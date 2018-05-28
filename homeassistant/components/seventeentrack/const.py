"""Constants for the 17track component."""
from datetime import timedelta
from logging import getLogger

DOMAIN = 'seventeentrack'
LOGGER = getLogger('homeassistant.components.seventeentrack')

DATA_SUBSCRIBERS = 'data_subscribers'
DATA_TOPIC_UPDATE = 'data_update'

CONF_DATA_OBJ = 'data_obj'
CONF_TRACKING_NUMBER = 'tracking_number'

DEFAULT_ATTRIBUTION = 'Data provided by 17track.net'
DEFAULT_REFRESH_INTERVAL = timedelta(hours=6)
