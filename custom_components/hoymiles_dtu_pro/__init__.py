"""Hoymiles DTU Pro"""
import logging
import voluptuous as vol
from homeassistant.components.sensor import (PLATFORM_SCHEMA)
import homeassistant.helpers.config_validation as cv
from homeassistant.const import (CONF_HOST, CONF_NAME, CONF_SCAN_INTERVAL)

from .sensor import HoymilesDTUSensor
from .DTUConnection import DTUConnection
from .const import (DEFAULT_NAME, DEFAULT_SCAN_INTERVAL, MONITORED_CONDITIONS,
                    MONITORED_CONDITIONS_PV, CONF_PANELS)

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST):
    cv.string,
    vol.Optional(CONF_PANELS, default=0):
    cv.byte,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME):
    cv.string,
    vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL):
    cv.time_period
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    name = config.get(CONF_NAME)
    host = config.get(CONF_HOST)
    panels = config.get(CONF_PANELS)
    scan_interval = config.get(CONF_SCAN_INTERVAL)

    updater = DTUConnection(host, panels, scan_interval)
    updater.update()
    _LOGGER.debug("[Hoymiles] Updater data: %s", updater.data)

    if updater.data is None:
        raise Exception('Invalid configuration for Hoymiles DTU platform')
    sensors = []
    for sensor_type in MONITORED_CONDITIONS:
        sensors.append(
            HoymilesDTUSensor(hass, name, sensor_type, panels, updater))

    for variable in MONITORED_CONDITIONS_PV:
        i = 1
        for i in range(panels):
            # sensors.append(
            #     HoymilesPVSensor(
            #      name, updater.data.microinverter_data[i - 1].serial_number,
            #      i, updater.data.microinverter_data[i - 1].port_number,
            #      variable, updater))
            continue
    add_entities(sensors, update_before_add=True)
