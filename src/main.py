import os
from enum import Enum
import logging
from typing import List, Union

import werkzeug.exceptions
from flask import Flask, jsonify, request, abort
from sun2000_modbus import inverter
from sun2000_modbus.datatypes import DataType
from sun2000_modbus.registers import InverterEquipmentRegister, BatteryEquipmentRegister, MeterEquipmentRegister

inverter_host = None
inverter_port = 6607
accepted_api_keys = []
log_level = os.getenv('LOG_LEVEL', 'INFO')

logger = logging.getLogger('sun2000-rest')
logger.setLevel(level=log_level)
app = Flask(__name__)


class Equipment(Enum):
    INVERTER = 'inverter'
    BATTERY = 'battery'
    METER = 'meter'


def validate_settings():
    global inverter_host
    global inverter_port
    global accepted_api_keys

    # INVERTER_HOST
    if os.getenv('INVERTER_HOST'):
        inverter_host = os.getenv('INVERTER_HOST')
    else:
        exit('Error: Required environment variable INVERTER_HOST not set')

    # INVERTER_PORT
    if os.getenv('INVERTER_PORT'):
        inverter_port = os.getenv('INVERTER_PORT')

    # ACCEPTED_API_KEYS
    if os.getenv('ACCEPTED_API_KEYS'):
        accepted_api_keys = os.getenv('ACCEPTED_API_KEYS').split(',')
    else:
        exit('Error: Required environment variable ACCEPTED_API_KEYS not set')


def validate_auth_header():
    api_key = request.headers.get('x-api-key')
    if api_key is None or api_key not in accepted_api_keys:
        abort(401, 'No or invalid API-key provided')


def validate_equipment(equipment_value: str) -> Equipment:
    logger.debug(f'Validating equipment value: {equipment_value}')
    if equipment_value is None:
        abort(400, 'No value for equipment')

    if equipment_value not in set(item.value for item in Equipment):
        abort(400, 'Invalid value for equipment')

    return Equipment(equipment_value)


def validate_registers(equipment: Equipment, register_names: List[str]) -> List[Union[InverterEquipmentRegister, BatteryEquipmentRegister, MeterEquipmentRegister]]:
    logger.debug(f'Validating registers for equipment {equipment}: {register_names}')
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


def get_register_data(register: Union[InverterEquipmentRegister, BatteryEquipmentRegister, MeterEquipmentRegister]) -> dict:
    logger.debug(f'Reading data for register {register.name}')
    if not inverter.connected:
        logger.debug("Connecting to inverter")
        inverter.connect()
    register_definition = register.value

    # name
    register_data = {'name': register.name}

    # type and value
    if register_definition.data_type == DataType.MULTIDATA:
        register_data.update({'type': 'string'})
        register_data.update({'value': inverter.read_raw_value(register).hex()})
    elif register_definition.data_type in (DataType.INT16_BE, DataType.UINT16_BE, DataType.INT32_BE, DataType.UINT32_BE):
        register_data.update({'type': 'number'})
        register_data.update({'value': str(inverter.read_raw_value(register))})
    else:
        register_data.update({'type': 'string'})
        register_data.update({'value': inverter.read_raw_value(register)})

    # gain
    if register_definition.gain is not None:
        register_data.update({'gain': register_definition.gain})

    # unit
    if register_definition.unit is not None:
        register_data.update({'unit': register_definition.unit})

    # mappedValue
    if register_definition.mapping is not None:
        register_data.update({'mappedValue': inverter.read_formatted(register)})

    return register_data


@app.get('/registers')
def get_registers():
    logger.debug('GET /registers called')
    validate_auth_header()

    equipment = validate_equipment(request.args.get('equipment'))

    registers = []
    if equipment == Equipment.INVERTER:
        registers = [item.name for item in InverterEquipmentRegister]
    elif equipment == Equipment.BATTERY:
        registers = [item.name for item in BatteryEquipmentRegister]
    elif equipment == Equipment.METER:
        registers = [item.name for item in MeterEquipmentRegister]

    response = {'equipment': equipment.value, 'registers': registers}

    return jsonify(response)


@app.post('/register-values')
def post_register_values():
    logger.debug('POST /register-values called')
    validate_auth_header()

    equipment = validate_equipment(request.get_json()['equipment'])
    register_names = request.get_json()['registers']
    registers = validate_registers(equipment, register_names)

    register_data = []
    for register in registers:
        register_data.append(get_register_data(register))

    response = {'equipment': equipment.value, 'registers': register_data}

    return jsonify(response)


@app.errorhandler(werkzeug.exceptions.HTTPException)
def handle_bad_request(error):
    logger.debug(f'Handling error {error}')
    response = jsonify({'message': error.description})
    response.status_code = error.code
    return response


# main
validate_settings()
logger.info('Initializing REST interface for Sun2000 inverter')
logger.info(f'Inverter will be contacted on: host = {inverter_host}, port = {inverter_port}')
logger.info(f'Log level set to {log_level}')
inverter = inverter.Sun2000(host=inverter_host, port=inverter_port)
inverter.connect()
if not inverter.connected:
    exit('Connection to inverter could not be established')
logger.info('Ready to accept requests')
