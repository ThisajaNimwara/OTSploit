#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Profinet DCP (Discovery and Configuration Protocol) implementation for Scapy.
"""

from scapy.all import *
from scapy.packet import Packet, bind_layers
from scapy.fields import *

# Profinet DCP Service IDs
DCP_SERVICE_ID_IDENTIFY_REQUEST = 0x05
DCP_SERVICE_ID_IDENTIFY_RESPONSE = 0x06
DCP_SERVICE_ID_GET_REQUEST = 0x03
DCP_SERVICE_ID_GET_RESPONSE = 0x04
DCP_SERVICE_ID_SET_REQUEST = 0x01
DCP_SERVICE_ID_SET_RESPONSE = 0x02

# Profinet DCP Service Types
DCP_SERVICE_TYPE_REQUEST = 0x00
DCP_SERVICE_TYPE_RESPONSE_SUCCESS = 0x01
DCP_SERVICE_TYPE_RESPONSE_UNSUPPORTED = 0x02

# Profinet DCP Block Types
DCP_BLOCK_TYPE_DEVICE_PROPERTIES = 0x02
DCP_BLOCK_TYPE_IP_PARAMETER = 0x05
DCP_BLOCK_TYPE_DEVICE_INITIATIVE = 0x06
DCP_BLOCK_TYPE_ALL_SELECTOR = 0xFF
DCP_BLOCK_TYPE_CONTROL = 0x06
DCP_BLOCK_TYPE_DEVICE_NAME_OF_STATION = 0x02
DCP_BLOCK_TYPE_DEVICE_MANUFACTURER_SPECIFIC = 0x04

class ProfinetIO(Packet):
    """Profinet IO frame."""
    name = "Profinet IO"
    fields_desc = [
        XShortField("frameID", 0xFEFE),
    ]

class PNDCPHeader(Packet):
    """Profinet DCP Header."""
    name = "Profinet DCP Header"
    fields_desc = [
        ByteField("ServiceID", 0x05),
        ByteField("ServiceType", 0x00),
        XIntField("XID", 0x00000000),
        XShortField("ResponseDelay", 0x0000),
        XShortField("DCPDataLength", 0x0000),
    ]

class PNDCPBlock(Packet):
    """Base Profinet DCP Block."""
    name = "Profinet DCP Block"
    fields_desc = [
        ByteField("Option", 0x00),
        ByteField("Suboption", 0x00),
        XShortField("BlockLength", 0x0000),
    ]

class PNDCPIdentRequest(PNDCPBlock):
    """Profinet DCP Identify Request Block."""
    name = "Profinet DCP Identify Request"
    fields_desc = [
        ByteField("Option", 0x02),
        ByteField("Suboption", 0x00),
        XShortField("BlockLength", 0x0000),
    ]

class PNDCPIdentDeviceNameOfStationResponseBlock(PNDCPBlock):
    """Profinet DCP Device Name of Station Response Block."""
    name = "Profinet DCP Device Name of Station Response"
    fields_desc = [
        ByteField("Option", 0x02),
        ByteField("Suboption", 0x02),
        XShortField("BlockLength", 0x0000),
        StrField("NameOfStation", ""),
    ]

class PNDCPIdentDeviceManufacturerSpecificResponseBlock(PNDCPBlock):
    """Profinet DCP Device Manufacturer Specific Response Block."""
    name = "Profinet DCP Device Manufacturer Specific Response"
    fields_desc = [
        ByteField("Option", 0x02),
        ByteField("Suboption", 0x04),
        XShortField("BlockLength", 0x0000),
        XIntField("DeviceVendorValue", 0x00000000),
    ]

class PNDCPIdentIPParameterResponseBlock(PNDCPBlock):
    """Profinet DCP IP Parameter Response Block."""
    name = "Profinet DCP IP Parameter Response"
    fields_desc = [
        ByteField("Option", 0x05),
        ByteField("Suboption", 0x01),
        XShortField("BlockLength", 0x0000),
        IPField("IPaddress", "0.0.0.0"),
        IPField("Subnetmask", "0.0.0.0"),
        IPField("StandardGateway", "0.0.0.0"),
    ]

# Bind layers
bind_layers(Ether, ProfinetIO, type=0x8892)
bind_layers(ProfinetIO, PNDCPHeader)
bind_layers(PNDCPHeader, PNDCPBlock)
