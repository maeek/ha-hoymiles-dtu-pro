import datetime
import logging
import voluptuous as vol
from homeassistant.components.sensor import (PLATFORM_SCHEMA, SensorEntity)
import homeassistant.helpers.config_validation as cv
from homeassistant.const import (CONF_HOST, CONF_NAME, CONF_SCAN_INTERVAL)

from .DTUConnection import DTUConnection
from .const import (DEFAULT_NAME, DEFAULT_SCAN_INTERVAL, DOMAIN,
                    MONITORED_CONDITIONS, CONF_PANELS, SENSOR_TYPES)

_LOGGER = logging.getLogger(__name__)

CONF_ALLOW_UNREACHABLE = "allow_unreachable"
DEFAULT_UNREACHABLE = False

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
    _LOGGER.debug("[Hoymiles] Updater data: %s", updater.data)

    sensors = []
    for sensor_type in MONITORED_CONDITIONS:
        sensors.append(
            HoymilesDTUSensor(hass, name, sensor_type, panels, host, updater))

    add_entities(sensors, update_before_add=True)


class HoymilesDTUSensor(SensorEntity):

    def __init__(self, hass, name, sensor_type, panels, host, updater):
        self._hass = hass
        self._client_name = name
        self._host = host
        self._type = sensor_type
        self._updater = updater
        self._name = SENSOR_TYPES[sensor_type][0]
        self._state = None
        self._last_state = None
        self._unit_of_measurement = SENSOR_TYPES[sensor_type][1]
        self._panels = panels

        self._device_info = {
            "identifiers": {(DOMAIN, name)},
            "name": name,
            "manufacturer": "Hoymiles",
            "model": "DTU Pro"
        }

    @property
    def name(self):
        return '{} {}'.format(self._client_name, self._type)

    @property
    def device_class(self):
        return SENSOR_TYPES[self._type][2]

    @property
    def state_class(self):
        return SENSOR_TYPES[self._type][3]

    @property
    def last_reset(self):
        if SENSOR_TYPES[self._type][4]:
            return datetime.now().replace(hour=0,
                                          minute=0,
                                          second=0,
                                          microsecond=0)

    @property
    def unit_of_measurement(self):
        return self._unit_of_measurement

    @property
    def state(self):
        if self._updater.data is not None and self._updater.data[
                self._type] is not None:
            _LOGGER.debug('[Hoymiles] State updated %s - %s', self._type,
                          self._updater.data[self._type])
            if self._type in ['power', 'total_energy', 'today_energy']:
                self._state = self._updater.data[self._type] / SENSOR_TYPES[
                    self._type][5]
            else:
                self._state = self._updater.data[self._type]

            self._last_state = self._state

        else:
            return self._last_state

        return self._state

    @property
    def unique_id(self) -> str:
        """Return the unique ID for this sensor."""
        return "_".join(
            [DOMAIN, self._host, self._client_name, self._name, "sensor"])

    def update(self):
        self._updater.update()

        if self._updater.data is None:
            return

        _LOGGER.debug('[Hoymiles] Updated %s - %s', self._type,
                      self._updater.data[self._type])

    @property
    def device_info(self):
        return self._device_info


# class HoymilesDTUPVSensor(SensorEntity):

#     def __init__(self, name, serial_number, panel_number, panel, sensor_type,
#                  updater):
#         self._hass = hass
#         self._client_name = name + ' ' + serial_number + ' PV ' + str(panel)
#         self._serial_number = serial_number
#         self._panel_number = panel_number
#         self._panel = panel
#         self._type = sensor_type
#         self._updater = updater
#         self._name = PV_TYPES[sensor_type][0]
#         self._state = None
#         self._unit_of_measurement = PV_TYPES[sensor_type][1]
#         self._panels = panels

#     @property
#     def name(self):
#         return '{} {}'.format(self._client_name, self._type)

#     @property
#     def device_class(self):
#         return PV_TYPES[self._type][2]

#     @property
#     def state_class(self):
#         return PV_TYPES[self._type][3]

#     @property
#     def last_reset(self):
#         if PV_TYPES[self._type][4]:
#             return datetime.now().replace(hour=0,
#                                           minute=0,
#                                           second=0,
#                                           microsecond=0)

#     @property
#     def unit_of_measurement(self):
#         return self._unit_of_measurement

#     @property
#     def state(self):
#         _LOGGER.debug('[Hoymiles] State updated %s - %s', self._type,
#                       self._updater.data[self._type])

#         # if self._updater.data[self._type] is not None:
#         #  if self._type in [
# 'current_power', 'total_energy', 'today_energy']:
#         #       self._state = self._updater.data[self._type] / PV_TYPES[
#         #             self._type][5]
#         #     else:
#         #         self._state = self._updater.data[self._type]
#         # return self._state
#         if (self._updater.data is not None
#                 and self._updater.data.total_production > 0):
#             temp = self._updater.data.panels_data[self._panel_number - 1]
#             self._state = temp[PV_TYPES[self._type][0]] / PV_TYPES[
#                 self._type][6]
#         elif (self._updater.data is not None
#               and self._updater.data.total_production == 0):
#             if PV_TYPES[self._type][7] == 0:
#                 self._state = 0
#             elif PV_TYPES[self._type][7] == 2 and datetime.now().hour == 0:
#                 self._state = 0
#         return self._state

#     def update(self):
#         self._updater.update()
#         _LOGGER.debug('[Hoymiles] Updated %s - %s', self._type,
#                       self._updater.data[self._type])
