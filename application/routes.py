import logging

import werkzeug.exceptions
from flask import Blueprint, jsonify, request, Response, abort
from flask import current_app as app
from sun2000_modbus.registers import InverterEquipmentRegister, BatteryEquipmentRegister, MeterEquipmentRegister

from application.util import Util, Equipment

utilities = Util(app)
bp = Blueprint('routes', __name__)


@bp.get('/registers')
def get_registers() -> Response:
    utilities.logger.debug('GET /registers called')
    utilities.validate_auth_header()

    equipment = utilities.validate_equipment(request.args.get('equipment'))

    registers = []
    if equipment == Equipment.INVERTER:
        registers = [item.name for item in InverterEquipmentRegister]
    elif equipment == Equipment.BATTERY:
        registers = [item.name for item in BatteryEquipmentRegister]
    elif equipment == Equipment.METER:
        registers = [item.name for item in MeterEquipmentRegister]

    response = {'equipment': equipment.value, 'registers': registers}

    return jsonify(response)


@bp.post('/register-values')
def post_register_values() -> Response:
    utilities.logger.debug('POST /register-values called')
    utilities.validate_auth_header()

    if 'equipment' not in request.get_json():
        abort(400, 'No value for equipment')
    equipment = utilities.validate_equipment(request.get_json()['equipment'])

    if 'registers' not in request.get_json():
        abort(400, 'No value for registers')
    register_names = request.get_json()['registers']
    registers = utilities.validate_registers(equipment, register_names)

    registers_data = utilities.get_registers_data(registers)
    response = {'equipment': equipment.value, 'registers': registers_data}

    return jsonify(response)


@bp.errorhandler(werkzeug.exceptions.HTTPException)
def handle_bad_request(error) -> Response:
    utilities.logger.debug(f'Handling error {error}')
    response = jsonify({'message': error.description})
    response.status_code = error.code
    return response


@bp.get('/health')
def get_health() -> Response:
    return Response(status=204)
