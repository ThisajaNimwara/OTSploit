#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WDB RPC Version 2 protocol implementation for Scapy.
"""

from scapy.all import *
from scapy.packet import Packet, bind_layers
from scapy.fields import *

# WDB RPC Version 2 Message Types
WDB_RPC2_MSG_TYPE_REQUEST = 0x00
WDB_RPC2_MSG_TYPE_RESPONSE = 0x01
WDB_RPC2_MSG_TYPE_ERROR = 0x02

# WDB RPC Version 2 Procedure IDs
WDB_RPC2_PROC_CONNECT = 0x00000001
WDB_RPC2_PROC_DISCONNECT = 0x00000002
WDB_RPC2_PROC_GET_SYMBOL = 0x00000003
WDB_RPC2_PROC_GET_SYMBOL_VALUE = 0x00000004
WDB_RPC2_PROC_SET_SYMBOL_VALUE = 0x00000005
WDB_RPC2_PROC_EXECUTE = 0x00000006

class WDBRPC2Header(Packet):
    """WDB RPC Version 2 Header."""
    name = "WDB RPC Version 2 Header"
    fields_desc = [
        XIntField("Version", 0x00000002),
        XIntField("MessageType", 0x00000000),
        XIntField("ProcedureID", 0x00000000),
        XIntField("TransactionID", 0x00000000),
        XIntField("DataLength", 0x00000000),
    ]

class WDBRPC2ConnectRequest(Packet):
    """WDB RPC Version 2 Connect Request."""
    name = "WDB RPC Version 2 Connect Request"
    fields_desc = [
        XIntField("ClientVersion", 0x00000001),
        XIntField("ProtocolVersion", 0x00000002),
        XIntField("ClientType", 0x00000001),
        XIntField("ClientFlags", 0x00000000),
        XIntField("ClientNameLength", 0x00000000),
        StrField("ClientName", ""),
    ]

class WDBRPC2ConnectResponse(Packet):
    """WDB RPC Version 2 Connect Response."""
    name = "WDB RPC Version 2 Connect Response"
    fields_desc = [
        XIntField("ServerVersion", 0x00000001),
        XIntField("ProtocolVersion", 0x00000002),
        XIntField("ServerType", 0x00000001),
        XIntField("ServerFlags", 0x00000000),
        XIntField("ServerNameLength", 0x00000000),
        StrField("ServerName", ""),
    ]

class WDBRPC2ExecuteRequest(Packet):
    """WDB RPC Version 2 Execute Request."""
    name = "WDB RPC Version 2 Execute Request"
    fields_desc = [
        XIntField("CommandLength", 0x00000000),
        StrField("Command", ""),
        XIntField("ArgumentCount", 0x00000000),
        StrField("Arguments", ""),
    ]

class WDBRPC2ExecuteResponse(Packet):
    """WDB RPC Version 2 Execute Response."""
    name = "WDB RPC Version 2 Execute Response"
    fields_desc = [
        XIntField("ReturnCode", 0x00000000),
        XIntField("OutputLength", 0x00000000),
        StrField("Output", ""),
        XIntField("ErrorLength", 0x00000000),
        StrField("Error", ""),
    ]

# Bind layers
bind_layers(IP, WDBRPC2Header, proto=6)
bind_layers(TCP, WDBRPC2Header, dport=17185)
bind_layers(TCP, WDBRPC2Header, sport=17185)
bind_layers(WDBRPC2Header, WDBRPC2ConnectRequest)
bind_layers(WDBRPC2Header, WDBRPC2ConnectResponse)
bind_layers(WDBRPC2Header, WDBRPC2ExecuteRequest)
bind_layers(WDBRPC2Header, WDBRPC2ExecuteResponse)
