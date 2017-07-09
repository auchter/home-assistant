import logging
import denonavr_serial

import voluptuous as vol

from homeassistant.components.media_player import (
    PLATFORM_SCHEMA, SUPPORT_TURN_OFF, SUPPORT_TURN_ON, SUPPORT_VOLUME_MUTE,
    SUPPORT_VOLUME_SET, SUPPORT_SELECT_SOURCE, MediaPlayerDevice)
from homeassistant.const import (
    CONF_PORT, CONF_NAME, STATE_OFF, STATE_ON, STATE_UNKNOWN)
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_PORT, default="/dev/ttyUSB0"): cv.string
})

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the Denon platform."""
    d = denonavr_serial.Avr3805(port=config.get(CONF_PORT))

    add_devices([DenonMain(d.main)])
    return True

class DenonMain(MediaPlayerDevice):
    def __init__(self, denon):
        self._denon = denon
        self._powered_on = False
        self._volume = 0.0
        self._muted = False
        self._source = None

    def update(self):
        with self._denon.denon.lock:
            self._powered_on = self._denon.powered_on()
            self._volume = self._denon.get_volume()
            self._muted = self._denon.muted()
            self._source = self._denon.get_source()

    @property
    def name(self):
        return "Stereo"

    @property
    def state(self):
        if self._powered_on:
            return STATE_ON
        else:
            return STATE_OFF

    @property
    def supported_features(self):
        return SUPPORT_VOLUME_SET | SUPPORT_VOLUME_MUTE | \
                SUPPORT_TURN_ON | SUPPORT_TURN_OFF | SUPPORT_SELECT_SOURCE

    @property
    def volume_level(self):
        return self._volume

    @property
    def is_volume_muted(self):
        return self._muted

    @property
    def source(self):
        return self._source

    @property
    def source_list(self):
        return self._denon.denon.sources

    def select_source(self, source):
        self._denon.set_source(source)
    
    def set_volume_level(self, volume):
        self._denon.set_volume(volume)

    def mute_volume(self, mute):
        if mute:
            self._denon.mute()
        else:
            self._denon.unmute()
    
    def turn_off(self):
        self._denon.power_off()

    def turn_on(self):
        self._denon.power_on()

    def volume_up(self):
        self._denon.volume_up()

    def volume_down(self):
        self._denon.volume_down()
