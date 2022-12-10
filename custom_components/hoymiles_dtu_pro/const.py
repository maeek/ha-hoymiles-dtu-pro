from datetime import timedelta
from homeassistant.const import (POWER_WATT, ENERGY_KILO_WATT_HOUR,
                                 DEVICE_CLASS_POWER, DEVICE_CLASS_ENERGY,
                                 ELECTRIC_CURRENT_AMPERE,
                                 ELECTRIC_POTENTIAL_VOLT, DEVICE_CLASS_VOLTAGE,
                                 DEVICE_CLASS_CURRENT, TEMP_CELSIUS,
                                 DEVICE_CLASS_TEMPERATURE)
from homeassistant.components.sensor import (STATE_CLASS_MEASUREMENT,
                                             STATE_CLASS_TOTAL,
                                             STATE_CLASS_TOTAL_INCREASING)

DOMAIN = "hoymiles_dtu_pro"
DEFAULT_NAME = 'Hoymiles DTU-Pro'
CONF_PANELS = "panels"
DEFAULT_SCAN_INTERVAL = timedelta(minutes=2)

# description, unit, device, class, reset, multiplier, keep values
# (0-none, 1-yes, 2-until midnight)
SENSOR_TYPES = {
    'power': [
        'Power', POWER_WATT, DEVICE_CLASS_POWER, STATE_CLASS_MEASUREMENT,
        False, 1, 0
    ],
    'today_energy': [
        'Energy today', ENERGY_KILO_WATT_HOUR, DEVICE_CLASS_ENERGY,
        STATE_CLASS_TOTAL_INCREASING, False, 1000, 2
    ],
    'total_energy': [
        'Energy lifetime', ENERGY_KILO_WATT_HOUR, DEVICE_CLASS_ENERGY,
        STATE_CLASS_TOTAL, False, 1000, 1
    ],
    'alarm_flag':
    ['Alarm flag', ' ', 'alarm_flag', STATE_CLASS_MEASUREMENT, False, 1, 0],
    'dtu_serial_number':
    ['DTU serial number', ' ', 'dtu_serial_number', None, False, None, 0]
}

PV_TYPES = {
    'pv_voltage': [
        3, 'Voltage', ELECTRIC_POTENTIAL_VOLT, DEVICE_CLASS_VOLTAGE,
        STATE_CLASS_MEASUREMENT, False, 1, 0
    ],
    'pv_current': [
        4, 'Current', ELECTRIC_CURRENT_AMPERE, DEVICE_CLASS_CURRENT,
        STATE_CLASS_MEASUREMENT, False, 1, 0
    ],
    'grid_voltage': [
        5, 'Grid voltage', ELECTRIC_POTENTIAL_VOLT, DEVICE_CLASS_VOLTAGE,
        STATE_CLASS_MEASUREMENT, False, 1, 0
    ],
    'pv_power': [
        7, 'Power', POWER_WATT, DEVICE_CLASS_POWER, STATE_CLASS_MEASUREMENT,
        False, 1, 0
    ],
    'pv_today_energy': [
        8, 'Energy today', ENERGY_KILO_WATT_HOUR, DEVICE_CLASS_ENERGY,
        STATE_CLASS_TOTAL_INCREASING, False, 1000, 2
    ],
    'pv_total_energy': [
        9, 'Energy lifetime', ENERGY_KILO_WATT_HOUR, DEVICE_CLASS_ENERGY,
        STATE_CLASS_TOTAL, False, 1000, 1
    ],
    'pv_temperature': [
        10, 'Temperature', TEMP_CELSIUS, DEVICE_CLASS_TEMPERATURE,
        STATE_CLASS_MEASUREMENT, False, 1, 0
    ],
    'pv_operating_status': [
        11, 'Status', ' ', 'operating_status', STATE_CLASS_MEASUREMENT, False,
        1, 0
    ],
    'pv_alarm_code': [
        12, 'Alarm Code', ' ', 'alarm_code', STATE_CLASS_MEASUREMENT, False, 1,
        0
    ],
    'pv_alarm_count': [
        13, 'Alarm Count', ' ', 'alarm_count', STATE_CLASS_MEASUREMENT, False,
        1, 0
    ],
    'pv_link_status': [
        14, 'Link status', ' ', 'link_status', STATE_CLASS_MEASUREMENT, False,
        1, 0
    ]
}

MONITORED_CONDITIONS = SENSOR_TYPES.keys()
MONITORED_CONDITIONS_PV = PV_TYPES.keys()
