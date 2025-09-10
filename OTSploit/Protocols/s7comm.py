#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
S7comm protocol implementation for Scapy.
"""

from scapy.all import *
from scapy.packet import Packet, bind_layers
from scapy.fields import *

# S7comm PDU Types
S7_PDU_TYPE_REQUEST = 0x01
S7_PDU_TYPE_RESPONSE = 0x03
S7_PDU_TYPE_USER_DATA = 0x07

# S7comm Function Codes
S7_FUNC_READ_VAR = 0x04
S7_FUNC_WRITE_VAR = 0x05
S7_FUNC_READ_SZL = 0x07
S7_FUNC_CPU_SERVICES = 0x08
S7_FUNC_DOWNLOAD = 0x1A
S7_FUNC_DOWNLOAD_BLOCK = 0x1B
S7_FUNC_UPLOAD = 0x1D
S7_FUNC_UPLOAD_BLOCK = 0x1E
S7_FUNC_PLC_STOP = 0x29
S7_FUNC_PLC_START = 0x28

class S7Header(Packet):
    """S7comm Header."""
    name = "S7comm Header"
    fields_desc = [
        ByteField("Version", 0x03),
        ByteField("Reserved1", 0x00),
        XShortField("Length", 0x0000),
        XShortField("PDUReference", 0x0000),
        ByteField("PDUType", 0x01),
        ByteField("Reserved2", 0x00),
        XShortField("ParameterLength", 0x0000),
        XShortField("DataLength", 0x0000),
        ByteField("ErrorClass", 0x00),
        ByteField("ErrorCode", 0x00),
    ]

class S7Parameter(Packet):
    """S7comm Parameter."""
    name = "S7comm Parameter"
    fields_desc = [
        ByteField("FunctionCode", 0x04),
        ByteField("ItemCount", 0x01),
    ]

class S7Data(Packet):
    """S7comm Data."""
    name = "S7comm Data"
    fields_desc = [
        ByteField("ReturnCode", 0x00),
        ByteField("TransportSize", 0x00),
        XShortField("Length", 0x0000),
        StrField("Data", ""),
    ]

class S7ReadVarRequest(S7Parameter):
    """S7comm Read Variable Request."""
    name = "S7comm Read Variable Request"
    fields_desc = [
        ByteField("FunctionCode", 0x04),
        ByteField("ItemCount", 0x01),
        ByteField("SpecificationType", 0x12),
        ByteField("LengthOfFollowing", 0x0A),
        ByteField("SyntaxID", 0x10),
        ByteField("TransportSize", 0x02),
        XShortField("Length", 0x0001),
        XShortField("DBNumber", 0x0000),
        ByteField("Area", 0x84),
        XShortField("Address", 0x0000),
    ]

class S7ReadVarResponse(S7Parameter):
    """S7comm Read Variable Response."""
    name = "S7comm Read Variable Response"
    fields_desc = [
        ByteField("FunctionCode", 0x04),
        ByteField("ItemCount", 0x01),
        ByteField("ReturnCode", 0x00),
        ByteField("TransportSize", 0x02),
        XShortField("Length", 0x0001),
        StrField("Data", ""),
    ]

class S7WriteVarRequest(S7Parameter):
    """S7comm Write Variable Request."""
    name = "S7comm Write Variable Request"
    fields_desc = [
        ByteField("FunctionCode", 0x05),
        ByteField("ItemCount", 0x01),
        ByteField("SpecificationType", 0x12),
        ByteField("LengthOfFollowing", 0x0A),
        ByteField("SyntaxID", 0x10),
        ByteField("TransportSize", 0x02),
        XShortField("Length", 0x0001),
        XShortField("DBNumber", 0x0000),
        ByteField("Area", 0x84),
        XShortField("Address", 0x0000),
        StrField("Data", ""),
    ]

class S7WriteVarResponse(S7Parameter):
    """S7comm Write Variable Response."""
    name = "S7comm Write Variable Response"
    fields_desc = [
        ByteField("FunctionCode", 0x05),
        ByteField("ItemCount", 0x01),
        ByteField("ReturnCode", 0x00),
    ]

class S7CPUControlRequest(S7Parameter):
    """S7comm CPU Control Request."""
    name = "S7comm CPU Control Request"
    fields_desc = [
        ByteField("FunctionCode", 0x28),
        ByteField("ParameterLength", 0x00),
        ByteField("DataLength", 0x00),
        ByteField("Mode", 0x01),
    ]

class S7CPUControlResponse(S7Parameter):
    """S7comm CPU Control Response."""
    name = "S7comm CPU Control Response"
    fields_desc = [
        ByteField("FunctionCode", 0x28),
        ByteField("ParameterLength", 0x00),
        ByteField("DataLength", 0x00),
        ByteField("ReturnCode", 0x00),
    ]

# Bind layers
bind_layers(IP, S7Header, proto=6)
bind_layers(TCP, S7Header, dport=102)
bind_layers(TCP, S7Header, sport=102)
bind_layers(S7Header, S7ReadVarRequest)
bind_layers(S7Header, S7ReadVarResponse)
bind_layers(S7Header, S7WriteVarRequest)
bind_layers(S7Header, S7WriteVarResponse)
bind_layers(S7Header, S7CPUControlRequest)
bind_layers(S7Header, S7CPUControlResponse)
