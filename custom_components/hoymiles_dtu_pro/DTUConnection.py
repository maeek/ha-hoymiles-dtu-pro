#!/usr/bin/python3
import logging
import time
from homeassistant.util import Throttle
from pymodbus.client import ModbusTcpClient

_LOGGER = logging.getLogger(__name__)

OFFSET_DTU_BASE = 0x2000
OFFSET_BASE = 0x1000
OFFSET_STEP = 0x28
MODBUS_PORT = 502
MAX_CONNECTION_RETRIES = 10
MAX_READ_RETRIES = 10


def unsigned2signed(unsigned_value):
    signed_value = unsigned_value if unsigned_value < (
        1 << 16 - 1) else unsigned_value - (1 << 16)
    return signed_value


class DTUConnection:

    def __init__(self, host, panels_number, scan_interval):
        self.host = host
        self.panels_number = panels_number
        self.update = Throttle(scan_interval)(self._update)
        self.data = None
        self.modbus_client = ModbusTcpClient(self.host, MODBUS_PORT)
        self.connection_retry = 0
        self.modbus_read_retry = 0

    def _read_pv_registers(self, panel_nr, retry=0):
        if retry == MAX_READ_RETRIES:
            _LOGGER.error("[%s][i-%d] Couldn't read registers", self.host,
                          panel_nr)
            return

        rr = self.modbus_client.read_holding_registers(
            OFFSET_BASE + OFFSET_STEP * panel_nr, 20)

        if rr.isError():
            retry += 1
            _LOGGER.error(
                "[%s][i-%d] Problem reading registers, retrying... (%d/%d)",
                self.host, panel_nr, retry, MAX_READ_RETRIES)
            return self._read_pv_registers(panel_nr, retry)

        if rr:
            return rr.registers
        return

    def _read_dtu_registers(self, retry=0):
        if retry == MAX_READ_RETRIES:
            _LOGGER.error("[%s][dtu] Couldn't read registers", self.host)
            return

        rr = self.modbus_client.read_holding_registers(OFFSET_DTU_BASE, 3)

        if rr.isError():
            retry += 1
            _LOGGER.error(
                "[%s][dtu] Problem reading registers, retrying... (%d/%d)",
                self.host, retry, MAX_READ_RETRIES)
            return self._read_dtu_registers(retry)

        if rr:
            return {
                'dtu_serial_number':
                str(hex(rr.registers[0]).split('x')[-1]) +
                str(hex(rr.registers[1]).split('x')[-1]) +
                str(hex(rr.registers[2]).split('x')[-1]),
            }
        return

    def _normalize_data(self, data, panel_nr):
        if data is None:
            _LOGGER.error("[%s][i-%d] No data from registries arrived",
                          self.host, panel_nr)
            return None

        panel_data = {
            'pv_serial_number': str(hex(data[3]).split('x')[-1]),
            'pv_voltage': data[4] / 10,
            'pv_current': data[5] / 100,
            'grid_voltage': data[6] / 10,
            'grid_freq': data[7] / 100,
            'pv_power': data[8] / 10,
            'pv_today_energy': data[9],
            # 'pv_total_energy1': data[10] * 10,
            # 'pv_total_energy2': data[11],
            'pv_total_energy': data[10] * 10 + data[11],
            'pv_temp': unsigned2signed(data[12]) / 10,
            'pv_operating_status': data[13],
            'pv_alarm_code': data[14],
            'pv_alarm_count': data[15],
            'pv_link_status': data[16],
        }

        return panel_data

    def _try_connect(self, retry=0):
        if retry == MAX_CONNECTION_RETRIES:
            _LOGGER.error("[%s] Couldn't connect to modbus", self.host)
            return False

        if self.modbus_client.connect():
            return True

        retry += 1
        _LOGGER.error("[%s] Failed to connect to modbus, retrying...",
                      self.host)
        time.sleep(1)
        return self._try_connect(retry)

    def _update(self):
        data = []

        if self._try_connect() is False:
            _LOGGER.error("[%s] Problem connecting to modbus", self.host)
            return

        for i in range(self.panels_number):
            data.append(self._normalize_data(self._read_pv_registers(i), i))

        dtu_device = self._read_dtu_registers()

        self.modbus_client.close()

        if data is None or len(data) != self.panels_number:
            return None

        self.data = {
            'dtu_serial_number': dtu_device['dtu_serial_number'],
            'today_energy': sum([i['pv_today_energy'] for i in data]),
            'total_energy': sum([i['pv_total_energy'] for i in data]),
            'power': sum([i['pv_power'] for i in data]),
            'alarm_flag': any([i['pv_alarm_code'] != 0 for i in data]),
            'panels_data': data,
        }

        _LOGGER.debug('[Hoymiles] Data arrived %s', self.data)

        return self.data


if __name__ == "__main__":
    dtu = DTUConnection("10.20.0.170", 16, 10)
    dtu.update()
    print(dtu.data)
