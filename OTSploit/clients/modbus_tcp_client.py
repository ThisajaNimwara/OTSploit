#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import struct
from scapy.all import *

class ModbusClient:
    """Modbus-TCP client for industrial devices."""
    
    def __init__(self, name="ModbusClient", ip="127.0.0.1", port=502):
        self.name = name
        self.ip = ip
        self.port = port
        self.sock = None
        self.connected = False
        self.transaction_id = 0
        
    def connect(self):
        """Connect to Modbus-TCP device."""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(10)
            self.sock.connect((self.ip, self.port))
            self.connected = True
            print(f"[INFO] [{self.name}.connect] Connected to {self.ip}:{self.port}")
            return True
        except Exception as e:
            print(f"[ERROR] [{self.name}.connect] Connection failed: {str(e)}")
            return False
    
    def disconnect(self):
        """Disconnect from Modbus-TCP device."""
        if self.sock:
            self.sock.close()
            self.connected = False
            print(f"[INFO] [{self.name}.disconnect] Disconnected from {self.ip}:{self.port}")
    
    def _send_request(self, function_code, data):
        """Send Modbus request."""
        if not self.connected:
            return None
        
        self.transaction_id += 1
        protocol_id = 0
        length = len(data) + 2
        unit_id = 1
        
        # Build Modbus header
        header = struct.pack('>HHHB', self.transaction_id, protocol_id, length, unit_id)
        packet = header + data
        
        try:
            self.sock.send(packet)
            response = self.sock.recv(1024)
            return response
        except Exception as e:
            print(f"[ERROR] [{self.name}._send_request] Failed: {str(e)}")
            return None
    
    def read_coils(self, address=0, count=1):
        """Read coils (discrete outputs)."""
        print(f"[*] Sending Modbus read coils request...")
        
        if not self.connected:
            return []
        
        # Function code 0x01 (Read Coils)
        function_code = 0x01
        data = struct.pack('>HH', address, count)
        
        response = self._send_request(function_code, data)
        if response and len(response) > 8:
            # Parse response
            byte_count = response[8]
            coil_data = response[9:9+byte_count]
            
            # Convert bytes to bit list
            coils = []
            for byte in coil_data:
                for bit in range(8):
                    coils.append(str((byte >> bit) & 1))
            
            return coils[:count]
        
        return ['0'] * count
    
    def read_holding_registers(self, address=0, count=1):
        """Read holding registers."""
        print(f"[*] Sending Modbus read holding registers request...")
        
        if not self.connected:
            return []
        
        # Function code 0x03 (Read Holding Registers)
        function_code = 0x03
        data = struct.pack('>HH', address, count)
        
        response = self._send_request(function_code, data)
        if response and len(response) > 8:
            # Parse response
            byte_count = response[8]
            register_data = response[9:9+byte_count]
            
            # Convert bytes to register values
            registers = []
            for i in range(0, len(register_data), 2):
                if i + 1 < len(register_data):
                    value = struct.unpack('>H', register_data[i:i+2])[0]
                    registers.append(value)
            
            return registers[:count]
        
        return [0] * count
    
    def read_input_registers(self, address=0, count=1):
        """Read input registers."""
        print(f"[*] Sending Modbus read input registers request...")
        
        if not self.connected:
            return []
        
        # Function code 0x04 (Read Input Registers)
        function_code = 0x04
        data = struct.pack('>HH', address, count)
        
        response = self._send_request(function_code, data)
        if response and len(response) > 8:
            # Parse response
            byte_count = response[8]
            register_data = response[9:9+byte_count]
            
            # Convert bytes to register values
            registers = []
            for i in range(0, len(register_data), 2):
                if i + 1 < len(register_data):
                    value = struct.unpack('>H', register_data[i:i+2])[0]
                    registers.append(value)
            
            return registers[:count]
        
        return [0] * count
    
    def write_multiple_coils(self, address=0, values=None):
        """Write multiple coils."""
        if values is None:
            values = []
        
        print(f"[*] Sending Modbus write coils request...")
        
        if not self.connected:
            return None
        
        # Function code 0x0F (Write Multiple Coils)
        function_code = 0x0F
        byte_count = (len(values) + 7) // 8
        
        # Convert bit list to bytes
        coil_bytes = bytearray(byte_count)
        for i, value in enumerate(values):
            if value:
                byte_index = i // 8
                bit_index = i % 8
                coil_bytes[byte_index] |= (1 << bit_index)
        
        data = struct.pack('>HHB', address, len(values), byte_count) + coil_bytes
        
        response = self._send_request(function_code, data)
        if response and len(response) >= 8:
            # Parse response
            ref_number = struct.unpack('>H', response[8:10])[0]
            bit_count = struct.unpack('>H', response[10:12])[0]
            return f"<ModbusHeaderResponse trans_id={self.transaction_id} proto_id=0 length=6 unit_id=1 |<WriteMultipleCoilsResponse ReferenceNumber={ref_number} BitCount={bit_count} |>>"
        
        return None
    
    def write_multiple_registers(self, address=0, values=None):
        """Write multiple registers."""
        if values is None:
            values = []
        
        print(f"[*] Sending Modbus write registers request...")
        
        if not self.connected:
            return None
        
        # Function code 0x10 (Write Multiple Registers)
        function_code = 0x10
        byte_count = len(values) * 2
        
        # Convert values to bytes
        register_bytes = bytearray()
        for value in values:
            register_bytes.extend(struct.pack('>H', value))
        
        data = struct.pack('>HHB', address, len(values), byte_count) + register_bytes
        
        response = self._send_request(function_code, data)
        if response and len(response) >= 8:
            # Parse response
            ref_number = struct.unpack('>H', response[8:10])[0]
            word_count = struct.unpack('>H', response[10:12])[0]
            return f"<ModbusHeaderResponse trans_id={self.transaction_id} proto_id=0 length=6 unit_id=1 |<WriteMultipleRegistersResponse ReferenceNumber={ref_number} WordCount={word_count} |>>"
        
        return None
