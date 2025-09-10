#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ethernet/IP (ENIP) protocol implementation for Scapy.
"""

from scapy.all import *
from scapy.packet import Packet, bind_layers
from scapy.fields import *

# Ethernet/IP Command IDs
ENIP_COMMAND_LIST_SERVICES = 0x0004
ENIP_COMMAND_LIST_IDENTITY = 0x0063
ENIP_COMMAND_LIST_INTERFACES = 0x0064
ENIP_COMMAND_REGISTER_SESSION = 0x0065
ENIP_COMMAND_UNREGISTER_SESSION = 0x0066
ENIP_COMMAND_SEND_RR_DATA = 0x006F
ENIP_COMMAND_SEND_UNIT_DATA = 0x0070

# Ethernet/IP Status Codes
ENIP_STATUS_SUCCESS = 0x0000
ENIP_STATUS_INVALID_COMMAND = 0x0001
ENIP_STATUS_INSUFFICIENT_MEMORY = 0x0002
ENIP_STATUS_INCORRECT_DATA = 0x0003
ENIP_STATUS_SESSION_HANDLE_INVALID = 0x0064
ENIP_STATUS_INVALID_LENGTH = 0x0065
ENIP_STATUS_UNSUPPORTED_PROTOCOL = 0x0069

class ENIPHeader(Packet):
    """Ethernet/IP Header."""
    name = "Ethernet/IP Header"
    fields_desc = [
        XShortField("Command", 0x0004),
        XShortField("Length", 0x0000),
        XIntField("SessionHandle", 0x00000000),
        XIntField("Status", 0x00000000),
        XLongField("SenderContext", 0x0000000000000000),
        XIntField("Options", 0x00000000),
    ]

class ENIPListServices(Packet):
    """Ethernet/IP List Services."""
    name = "Ethernet/IP List Services"
    fields_desc = [
        XShortField("ItemCount", 0x0000),
    ]

class ENIPListServicesItem(Packet):
    """Ethernet/IP List Services Item."""
    name = "Ethernet/IP List Services Item"
    fields_desc = [
        XShortField("ItemTypeCode", 0x0000),
        XShortField("ItemLength", 0x0000),
        XShortField("Version", 0x0000),
        XShortField("CapabilityFlags", 0x0000),
        XShortField("ServiceNameLength", 0x0000),
        StrField("ServiceName", ""),
    ]

class ENIPListIdentity(Packet):
    """Ethernet/IP List Identity."""
    name = "Ethernet/IP List Identity"
    fields_desc = [
        XShortField("ItemCount", 0x0000),
    ]

class ENIPListIdentityItem(Packet):
    """Ethernet/IP List Identity Item."""
    name = "Ethernet/IP List Identity Item"
    fields_desc = [
        XShortField("ItemTypeCode", 0x0000),
        XShortField("ItemLength", 0x0000),
        XShortField("EncapsulationProtocolVersion", 0x0000),
        XShortField("SocketAddressFamily", 0x0000),
        XShortField("SocketAddressPort", 0x0000),
        IPField("SocketAddressAddress", "0.0.0.0"),
        XShortField("SocketAddressZero", 0x0000),
        XShortField("VendorID", 0x0000),
        XShortField("DeviceType", 0x0000),
        XShortField("ProductCode", 0x0000),
        XShortField("Revision", 0x0000),
        XShortField("Status", 0x0000),
        XIntField("SerialNumber", 0x00000000),
        XShortField("ProductNameLength", 0x0000),
        StrField("ProductName", ""),
        XShortField("State", 0x0000),
    ]

# Bind layers
bind_layers(Ether, ENIPHeader, type=0x00E1)
bind_layers(ENIPHeader, ENIPListServices)
bind_layers(ENIPHeader, ENIPListIdentity)
bind_layers(ENIPListServices, ENIPListServicesItem)
bind_layers(ENIPListIdentity, ENIPListIdentityItem)
