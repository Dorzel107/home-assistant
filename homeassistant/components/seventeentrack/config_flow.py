"""Config flow to configure the 17track component."""

import voluptuous as vol

from homeassistant import config_entries, data_entry_flow
from homeassistant.core import callback
from homeassistant.util import slugify

from .const import CONF_TRACKING_NUMBER, DOMAIN


@callback
def configured_tracking_numbers(hass):
    """Return a set of the configured hosts."""
    return set((slugify(entry.data[CONF_TRACKING_NUMBER])) for
               entry in hass.config_entries.async_entries(DOMAIN))


@config_entries.HANDLERS.register(DOMAIN)
class SeventeenTrackFlowHandler(data_entry_flow.FlowHandler):
    """Define a 17track config flow."""

    VERSION = 1

    def __init__(self):
        """Initialize."""
        pass

    async def async_step_init(self, user_input=None):
        """Handle a flow start."""
        errors = {}

        if user_input is not None:
            key = slugify(user_input[CONF_TRACKING_NUMBER])
            if key not in configured_tracking_numbers(self.hass):
                return self.async_create_entry(
                    title=user_input[CONF_TRACKING_NUMBER],
                    data=user_input,
                )
            errors['base'] = 'name_exists'

        return self.async_show_form(
            step_id='init',
            data_schema=vol.Schema({
                vol.Required(CONF_TRACKING_NUMBER): str,
            }),
            errors=errors,
        )
