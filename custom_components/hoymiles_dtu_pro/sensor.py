import logging
import datetime
from homeassistant.components.sensor import (SensorEntity)
from .const import (PV_TYPES, SENSOR_TYPES)

_LOGGER = logging.getLogger(__name__)


class HoymilesDTUSensor(SensorEntity):

    def __init__(self, hass, name, sensor_type, panels, updater):
        self._hass = hass
        self._client_name = name
        self._type = sensor_type
        self._updater = updater
        self._name = SENSOR_TYPES[sensor_type][0]
        self._state = None
        self._unit_of_measurement = SENSOR_TYPES[sensor_type][1]
        self._panels = panels

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
        _LOGGER.debug('[Hoymiles] State updated %s - %s', self._type,
                      self._updater.data[self._type])
        if self._updater.data[self._type] is not None:
            if self._type in ['current_power', 'total_energy', 'today_energy']:
                self._state = self._updater.data[self._type] / SENSOR_TYPES[
                    self._type][5]
            else:
                self._state = self._updater.data[self._type]
        return self._state

    def update(self):
        self._updater.update()
        _LOGGER.debug('[Hoymiles] Updated %s - %s', self._type,
                      self._updater.data[self._type])


class HoymilesDTUPVSensor(SensorEntity):

    def __init__(self, name, serial_number, panel_number, panel, sensor_type,
                 updater):
        self._hass = hass
        self._client_name = name + ' ' + serial_number + ' PV ' + str(panel)
        self._serial_number = serial_number
        self._panel_number = panel_number
        self._panel = panel
        self._type = sensor_type
        self._updater = updater
        self._name = PV_TYPES[sensor_type][0]
        self._state = None
        self._unit_of_measurement = PV_TYPES[sensor_type][1]
        self._panels = panels

    @property
    def name(self):
        return '{} {}'.format(self._client_name, self._type)

    @property
    def device_class(self):
        return PV_TYPES[self._type][2]

    @property
    def state_class(self):
        return PV_TYPES[self._type][3]

    @property
    def last_reset(self):
        if PV_TYPES[self._type][4]:
            return datetime.now().replace(hour=0,
                                          minute=0,
                                          second=0,
                                          microsecond=0)

    @property
    def unit_of_measurement(self):
        return self._unit_of_measurement

    @property
    def state(self):
        _LOGGER.debug('[Hoymiles] State updated %s - %s', self._type,
                      self._updater.data[self._type])

        # if self._updater.data[self._type] is not None:
        #  if self._type in ['current_power', 'total_energy', 'today_energy']:
        #       self._state = self._updater.data[self._type] / PV_TYPES[
        #             self._type][5]
        #     else:
        #         self._state = self._updater.data[self._type]
        # return self._state
        if (self._updater.data is not None
                and self._updater.data.total_production > 0):
            temp = self._updater.data.panels_data[self._panel_number - 1]
            self._state = temp[PV_TYPES[self._type][0]] / PV_TYPES[
                self._type][6]
        elif (self._updater.data is not None
              and self._updater.data.total_production == 0):
            if PV_TYPES[self._type][7] == 0:
                self._state = 0
            elif PV_TYPES[self._type][7] == 2 and datetime.now().hour == 0:
                self._state = 0
        return self._state

    def update(self):
        self._updater.update()
        _LOGGER.debug('[Hoymiles] Updated %s - %s', self._type,
                      self._updater.data[self._type])
