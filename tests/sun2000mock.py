from sun2000_modbus.registers import InverterEquipmentRegister, BatteryEquipmentRegister, MeterEquipmentRegister


def connect_success(self):
    self.connected = True


def connect_fail(self):
    self.connected = False


MockedRawResponses = {
    InverterEquipmentRegister.Model: 'SUN2000',
    InverterEquipmentRegister.RatedPower: 10000,
    InverterEquipmentRegister.State1: '0000000000000110',
    InverterEquipmentRegister.DeviceStatus: 512,
    InverterEquipmentRegister.QUCharacteristicCurve: b'\x00\x04\x03\xa2\x01\xb4\x03\xca\x00\x00\x04\x06\x00\x00\x04.\xfeL\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
    BatteryEquipmentRegister.TotalCharge: 548542,
    BatteryEquipmentRegister.SwitchToOffGrid: 0,
    MeterEquipmentRegister.MeterType: 1,
    MeterEquipmentRegister.CPhaseVoltage: 2356
}


def mock_read_raw_value(self, register):
    return MockedRawResponses[register]
