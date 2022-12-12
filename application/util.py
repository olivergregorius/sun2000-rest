import logging
from enum import Enum
from typing import List, Union

from flask import Flask, Config
from flask import request, abort
from sun2000_modbus import inverter
from sun2000_modbus.datatypes import DataType
from sun2000_modbus.inverter import Sun2000
from sun2000_modbus.registers import InverterEquipmentRegister, BatteryEquipmentRegister, MeterEquipmentRegister

from .constants import ENV_INVERTER_HOST, ENV_INVERTER_PORT, ENV_ACCEPTED_API_KEYS, ENV_LOG_LEVEL


class Equipment(Enum):
    INVERTER = 'inverter'
    BATTERY = 'battery'
    METER = 'meter'


class Util:
    config: Config
    logger: logging.Logger
    sun2000: Sun2000

    def __init__(self, app: Flask):
        self.config = app.config

        self.logger = logging.getLogger()
        self.logger.setLevel(self.config[ENV_LOG_LEVEL])
        self.logger.info('Initializing REST interface for Sun2000 inverter')
        self.logger.info(f'Inverter will be contacted on: host = {self.config[ENV_INVERTER_HOST]}, port = {self.config[ENV_INVERTER_PORT]}')
        self.logger.info(f'Log level set to {self.config[ENV_LOG_LEVEL]}')

        self.sun2000 = inverter.Sun2000(self.config[ENV_INVERTER_HOST], self.config[ENV_INVERTER_PORT])
        self.sun2000.connect()
        if not self.sun2000.connected:
            exit('Connection to inverter could not be established')

        self.logger.info('Ready to accept requests')

    def validate_auth_header(self) -> None:
        api_key = request.headers.get('x-api-key')
        if api_key is None or api_key not in self.config[ENV_ACCEPTED_API_KEYS]:
            abort(401, 'No or invalid API-key provided')

    def validate_equipment(self, equipment_value: str) -> Equipment:
        self.logger.debug(f'Validating equipment value: {equipment_value}')
        if equipment_value is None or len(equipment_value) == 0:
            abort(400, 'No value for equipment')

        if equipment_value not in set(item.value for item in Equipment):
            abort(400, 'Invalid value for equipment')

        return Equipment(equipment_value)

    def validate_registers(self, equipment: Equipment, register_names: List[str]) -> List[Union[InverterEquipmentRegister, BatteryEquipmentRegister, MeterEquipmentRegister]]:
        self.logger.debug(f'Validating registers for equipment {equipment}: {register_names}')
        if len(register_names) == 0:
            abort(400, 'No value for registers')

        if equipment == Equipment.INVERTER:
            register_members = InverterEquipmentRegister.__members__
        elif equipment == Equipment.BATTERY:
            register_members = BatteryEquipmentRegister.__members__
        else:
            register_members = MeterEquipmentRegister.__members__

        registers = []
        for register_name in register_names:
            if register_name not in register_members:
                abort(400, 'At least one invalid register passed')
            registers.append(register_members.__getitem__(register_name))

        return registers

    def get_register_data(self, register: Union[InverterEquipmentRegister, BatteryEquipmentRegister, MeterEquipmentRegister]) -> dict:
        self.logger.debug(f'Reading data for register {register.name}')
        register_definition = register.value

        # name
        register_data = {'name': register.name}

        # type and value
        if register_definition.data_type == DataType.MULTIDATA:
            register_data.update({'type': 'string'})
            register_data.update({'value': self.sun2000.read_raw_value(register).hex()})
        elif register_definition.data_type in (DataType.INT16_BE, DataType.UINT16_BE, DataType.INT32_BE, DataType.UINT32_BE):
            register_data.update({'type': 'number'})
            register_data.update({'value': str(self.sun2000.read_raw_value(register))})
        else:
            register_data.update({'type': 'string'})
            register_data.update({'value': self.sun2000.read_raw_value(register)})

        # gain
        if register_definition.gain is not None:
            register_data.update({'gain': register_definition.gain})

        # unit
        if register_definition.unit is not None:
            register_data.update({'unit': register_definition.unit})

        # mappedValue
        if register_definition.mapping is not None:
            register_data.update({'mappedValue': self.sun2000.read_formatted(register)})

        return register_data
