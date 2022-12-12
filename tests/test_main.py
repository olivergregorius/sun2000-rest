import json
import unittest
from unittest.mock import patch

import sun2000mock

from application import create_app


class MainTest(unittest.TestCase):

    @patch(
        'sun2000_modbus.inverter.Sun2000.connect', sun2000mock.connect_success
    )
    def setUp(self) -> None:
        test_config = {
            'INVERTER_HOST': '192.168.200.1',
            'INVERTER_PORT': 6607,
            'ACCEPTED_API_KEYS': '12345,98765',
            'LOG_LEVEL': 'DEBUG'
        }
        app = create_app(test_config)
        self.client = app.test_client()

    def test_unauthorized_access_to_GET_registers_returns_401(self) -> None:
        response = self.client.get('/registers', query_string={'equipment': 'inverter'})

        self.assertEqual(401, response.status_code)
        self.assertEqual({'message': 'No or invalid API-key provided'}, response.get_json())

    def test_any_api_key_is_valid(self) -> None:
        # Testing first API Key 12345
        response = self.client.get('/registers', query_string={'equipment': 'inverter'}, headers={'x-api-key': '12345'})

        self.assertEqual(200, response.status_code)

        # Testing second API Key 98765
        response = self.client.get('/registers', query_string={'equipment': 'inverter'}, headers={'x-api-key': '98765'})

        self.assertEqual(200, response.status_code)

    def test_providing_no_or_invalid_equipment_calling_GET_registers_returns_400(self) -> None:
        # Passing no equipment at all
        response = self.client.get('/registers', headers={'x-api-key': '12345'})

        self.assertEqual(400, response.status_code)
        self.assertEqual({'message': 'No value for equipment'}, response.get_json())

        # Passing an empty value for equipment
        response = self.client.get('/registers', query_string={'equipment': ''}, headers={'x-api-key': '12345'})

        self.assertEqual(400, response.status_code)
        self.assertEqual({'message': 'No value for equipment'}, response.get_json())

        # Passing an invalid equipment value
        response = self.client.get('/registers', query_string={'equipment': 'invalid_equipment'}, headers={'x-api-key': '12345'})

        self.assertEqual(400, response.status_code)
        self.assertEqual({'message': 'Invalid value for equipment'}, response.get_json())

    def test_calling_GET_registers_returns_registers_for_requested_equipment(self) -> None:
        # Equipment: inverter
        response = self.client.get('/registers', query_string={'equipment': 'inverter'}, headers={'x-api-key': '12345'})

        self.assertEqual(200, response.status_code)
        self.assertEqual('inverter', response.get_json()['equipment'])
        self.assertIn('Model', response.get_json()['registers'])
        self.assertIn('State1', response.get_json()['registers'])
        self.assertIn('InputPower', response.get_json()['registers'])
        self.assertNotIn('RunningStatus', response.get_json()['registers'])
        self.assertNotIn('SOC', response.get_json()['registers'])
        self.assertNotIn('Unit1BatteryPack2TotalCharge', response.get_json()['registers'])
        self.assertNotIn('MeterStatus', response.get_json()['registers'])
        self.assertNotIn('BPhaseVoltage', response.get_json()['registers'])
        self.assertNotIn('ABLineVoltage', response.get_json()['registers'])

        # Equipment: battery
        response = self.client.get('/registers', query_string={'equipment': 'battery'}, headers={'x-api-key': '12345'})

        self.assertEqual(200, response.status_code)
        self.assertEqual('battery', response.get_json()['equipment'])
        self.assertNotIn('Model', response.get_json()['registers'])
        self.assertNotIn('State1', response.get_json()['registers'])
        self.assertNotIn('InputPower', response.get_json()['registers'])
        self.assertIn('RunningStatus', response.get_json()['registers'])
        self.assertIn('SOC', response.get_json()['registers'])
        self.assertIn('Unit1BatteryPack2TotalCharge', response.get_json()['registers'])
        self.assertNotIn('MeterStatus', response.get_json()['registers'])
        self.assertNotIn('BPhaseVoltage', response.get_json()['registers'])
        self.assertNotIn('ABLineVoltage', response.get_json()['registers'])

        # Equipment: meter
        response = self.client.get('/registers', query_string={'equipment': 'meter'}, headers={'x-api-key': '12345'})

        self.assertEqual(200, response.status_code)
        self.assertEqual('meter', response.get_json()['equipment'])
        self.assertNotIn('Model', response.get_json()['registers'])
        self.assertNotIn('State1', response.get_json()['registers'])
        self.assertNotIn('InputPower', response.get_json()['registers'])
        self.assertNotIn('RunningStatus', response.get_json()['registers'])
        self.assertNotIn('SOC', response.get_json()['registers'])
        self.assertNotIn('Unit1BatteryPack2TotalCharge', response.get_json()['registers'])
        self.assertIn('MeterStatus', response.get_json()['registers'])
        self.assertIn('BPhaseVoltage', response.get_json()['registers'])
        self.assertIn('ABLineVoltage', response.get_json()['registers'])

    def test_providing_no_or_invalid_equipment_calling_POST_registervalues_returns_400(self) -> None:
        registers = ['Model']

        # Passing no equipment at all
        response = self.client.post('/register-values', data=json.dumps({'registers': registers}), content_type='application/json',
                                    headers={'x-api-key': '12345'})

        self.assertEqual(400, response.status_code)
        self.assertEqual({'message': 'No value for equipment'}, response.get_json())

        # Passing an empty value for equipment
        response = self.client.post('/register-values', data=json.dumps({'equipment': '', 'registers': registers}), content_type='application/json',
                                    headers={'x-api-key': '12345'})

        self.assertEqual(400, response.status_code)
        self.assertEqual({'message': 'No value for equipment'}, response.get_json())

        # Passing an invalid equipment value
        response = self.client.post('/register-values', data=json.dumps({'equipment': 'invalid_equipment', 'registers': registers}),
                                    content_type='application/json', headers={'x-api-key': '12345'})

        self.assertEqual(400, response.status_code)
        self.assertEqual({'message': 'Invalid value for equipment'}, response.get_json())

    def test_providing_no_or_invalid_registers_calling_POST_registervalues_returns_400(self) -> None:
        # Passing no registers at all
        response = self.client.post('/register-values', data=json.dumps({'equipment': 'inverter'}), content_type='application/json',
                                    headers={'x-api-key': '12345'})

        self.assertEqual(400, response.status_code)
        self.assertEqual({'message': 'No value for registers'}, response.get_json())

        # Passing an empty registers list
        registers = []
        response = self.client.post('/register-values', data=json.dumps({'equipment': 'inverter', 'registers': registers}), content_type='application/json',
                                    headers={'x-api-key': '12345'})

        self.assertEqual(400, response.status_code)
        self.assertEqual({'message': 'No value for registers'}, response.get_json())

        # Passing a list of registers containing one invalid register
        registers = ['Model', 'SN', 'RunningStatus']
        response = self.client.post('/register-values', data=json.dumps({'equipment': 'inverter', 'registers': registers}), content_type='application/json',
                                    headers={'x-api-key': '12345'})

        self.assertEqual(400, response.status_code)
        self.assertEqual({'message': 'At least one invalid register passed'}, response.get_json())

    @patch(
        'sun2000_modbus.inverter.Sun2000.read_raw_value', sun2000mock.mock_read_raw_value
    )
    def test_calling_POST_registervalues_for_inverter_equipment_returns_requested_register_values(self) -> None:
        registers = ['Model', 'RatedPower', 'State1', 'DeviceStatus', 'QUCharacteristicCurve']
        response = self.client.post('/register-values', data=json.dumps({'equipment': 'inverter', 'registers': registers}), content_type='application/json',
                                    headers={'x-api-key': '12345'})

        expected_response_json = {
            'equipment': 'inverter',
            'registers': [
                {
                    'name': 'Model',
                    'type': 'string',
                    'value': 'SUN2000'
                },
                {
                    'name': 'RatedPower',
                    'type': 'number',
                    'unit': 'kW',
                    'value': '10000',
                    'gain': 1000
                },
                {
                    'name': 'State1',
                    'type': 'string',
                    'value': '0000000000000110'
                },
                {
                    'name': 'DeviceStatus',
                    'type': 'number',
                    'value': '512',
                    'gain': 1,
                    'mappedValue': 'On-grid'
                },
                {
                    'name': 'QUCharacteristicCurve',
                    'type': 'string',
                    'value': '000403a201b403ca000004060000042efe4c000000000000000000000000000000000000000000000000'
                }
            ]
        }

        self.assertEqual(200, response.status_code)
        self.assertEqual(expected_response_json, response.get_json())

    @patch(
        'sun2000_modbus.inverter.Sun2000.read_raw_value', sun2000mock.mock_read_raw_value
    )
    def test_calling_POST_registervalues_for_battery_equipment_returns_requested_register_values(self) -> None:
        registers = ['TotalCharge', 'SwitchToOffGrid']
        response = self.client.post('/register-values', data=json.dumps({'equipment': 'battery', 'registers': registers}), content_type='application/json',
                                    headers={'x-api-key': '12345'})

        expected_response_json = {
            'equipment': 'battery',
            'registers': [
                {
                    'name': 'TotalCharge',
                    'type': 'number',
                    'unit': 'kWh',
                    'value': '548542',
                    'gain': 100
                },
                {
                    'name': 'SwitchToOffGrid',
                    'type': 'number',
                    'value': '0',
                    'gain': 1,
                    'mappedValue': 'Switch from grid-tied to off-grid'
                }
            ]
        }

        self.assertEqual(200, response.status_code)
        self.assertEqual(expected_response_json, response.get_json())

    @patch(
        'sun2000_modbus.inverter.Sun2000.read_raw_value', sun2000mock.mock_read_raw_value
    )
    def test_calling_POST_registervalues_for_meter_equipment_returns_requested_register_values(self) -> None:
        registers = ['MeterType', 'CPhaseVoltage']
        response = self.client.post('/register-values', data=json.dumps({'equipment': 'meter', 'registers': registers}), content_type='application/json',
                                    headers={'x-api-key': '12345'})

        expected_response_json = {
            'equipment': 'meter',
            'registers': [
                {
                    'name': 'MeterType',
                    'type': 'number',
                    'value': '1',
                    'gain': 1,
                    'mappedValue': 'three-phase'
                },
                {
                    'name': 'CPhaseVoltage',
                    'type': 'number',
                    'unit': 'V',
                    'value': '2356',
                    'gain': 10
                }

            ]
        }

        self.assertEqual(200, response.status_code)
        self.assertEqual(expected_response_json, response.get_json())

    def test_calling_GET_health_returns_204(self) -> None:
        response = self.client.get('/health')

        self.assertEqual(204, response.status_code)


class ConnectionFailTest(unittest.TestCase):

    @patch(
        'sun2000_modbus.inverter.Sun2000.connect', sun2000mock.connect_fail
    )
    def test_connection_to_inverter_fails_application_exits(self) -> None:
        test_config = {
            'INVERTER_HOST': '192.168.200.1',
            'INVERTER_PORT': 6607,
            'ACCEPTED_API_KEYS': '12345,98765',
            'LOG_LEVEL': 'DEBUG'
        }
        with self.assertRaises(SystemExit) as e:
            create_app(test_config)

        self.assertEqual('Connection to inverter could not be established', e.exception.code)
