#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modbus TCP protocol implementation for Scapy.
"""

from scapy.all import *
from scapy.packet import Packet, bind_layers
from scapy.fields import *

# Modbus Function Codes
MODBUS_FUNC_READ_COILS = 0x01
MODBUS_FUNC_READ_DISCRETE_INPUTS = 0x02
MODBUS_FUNC_READ_HOLDING_REGISTERS = 0x03
MODBUS_FUNC_READ_INPUT_REGISTERS = 0x04
MODBUS_FUNC_WRITE_SINGLE_COIL = 0x05
MODBUS_FUNC_WRITE_SINGLE_REGISTER = 0x06
MODBUS_FUNC_WRITE_MULTIPLE_COILS = 0x0F
MODBUS_FUNC_WRITE_MULTIPLE_REGISTERS = 0x10

class ModbusHeader(Packet):
    """Modbus TCP Header."""
    name = "Modbus TCP Header"
    fields_desc = [
        XShortField("TransactionID", 0x0000),
        XShortField("ProtocolID", 0x0000),
        XShortField("Length", 0x0000),
        ByteField("UnitID", 0x01),
    ]

class ModbusRequest(Packet):
    """Base Modbus Request."""
    name = "Modbus Request"
    fields_desc = [
        ByteField("FunctionCode", 0x01),
    ]

class ModbusResponse(Packet):
    """Base Modbus Response."""
    name = "Modbus Response"
    fields_desc = [
        ByteField("FunctionCode", 0x01),
    ]

class ReadCoilsRequest(ModbusRequest):
    """Modbus Read Coils Request."""
    name = "Modbus Read Coils Request"
    fields_desc = [
        ByteField("FunctionCode", 0x01),
        XShortField("StartingAddress", 0x0000),
        XShortField("QuantityOfCoils", 0x0001),
    ]

class ReadCoilsResponse(ModbusResponse):
    """Modbus Read Coils Response."""
    name = "Modbus Read Coils Response"
    fields_desc = [
        ByteField("FunctionCode", 0x01),
        ByteField("ByteCount", 0x00),
        StrField("CoilStatus", ""),
    ]

class ReadHoldingRegistersRequest(ModbusRequest):
    """Modbus Read Holding Registers Request."""
    name = "Modbus Read Holding Registers Request"
    fields_desc = [
        ByteField("FunctionCode", 0x03),
        XShortField("StartingAddress", 0x0000),
        XShortField("QuantityOfRegisters", 0x0001),
    ]

class ReadHoldingRegistersResponse(ModbusResponse):
    """Modbus Read Holding Registers Response."""
    name = "Modbus Read Holding Registers Response"
    fields_desc = [
        ByteField("FunctionCode", 0x03),
        ByteField("ByteCount", 0x00),
        StrField("RegisterValue", ""),
    ]

class WriteMultipleCoilsRequest(ModbusRequest):
    """Modbus Write Multiple Coils Request."""
    name = "Modbus Write Multiple Coils Request"
    fields_desc = [
        ByteField("FunctionCode", 0x0F),
        XShortField("StartingAddress", 0x0000),
        XShortField("QuantityOfOutputs", 0x0001),
        ByteField("ByteCount", 0x00),
        StrField("OutputsValue", ""),
    ]

class WriteMultipleCoilsResponse(ModbusResponse):
    """Modbus Write Multiple Coils Response."""
    name = "Modbus Write Multiple Coils Response"
    fields_desc = [
        ByteField("FunctionCode", 0x0F),
        XShortField("StartingAddress", 0x0000),
        XShortField("QuantityOfOutputs", 0x0001),
    ]

class WriteMultipleRegistersRequest(ModbusRequest):
    """Modbus Write Multiple Registers Request."""
    name = "Modbus Write Multiple Registers Request"
    fields_desc = [
        ByteField("FunctionCode", 0x10),
        XShortField("StartingAddress", 0x0000),
        XShortField("QuantityOfRegisters", 0x0001),
        ByteField("ByteCount", 0x00),
        StrField("RegistersValue", ""),
    ]

class WriteMultipleRegistersResponse(ModbusResponse):
    """Modbus Write Multiple Registers Response."""
    name = "Modbus Write Multiple Registers Response"
    fields_desc = [
        ByteField("FunctionCode", 0x10),
        XShortField("StartingAddress", 0x0000),
        XShortField("QuantityOfRegisters", 0x0001),
    ]

# Bind layers
bind_layers(IP, ModbusHeader, proto=6)
bind_layers(TCP, ModbusHeader, dport=502)
bind_layers(TCP, ModbusHeader, sport=502)
bind_layers(ModbusHeader, ReadCoilsRequest)
bind_layers(ModbusHeader, ReadCoilsResponse)
bind_layers(ModbusHeader, ReadHoldingRegistersRequest)
bind_layers(ModbusHeader, ReadHoldingRegistersResponse)
bind_layers(ModbusHeader, WriteMultipleCoilsRequest)
bind_layers(ModbusHeader, WriteMultipleCoilsResponse)
bind_layers(ModbusHeader, WriteMultipleRegistersRequest)
bind_layers(ModbusHeader, WriteMultipleRegistersResponse)
