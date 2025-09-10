#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OTSploitMCP - Minimal HTTP bridge to expose OTSploit operations for IDEs.

Endpoints (all JSON):
- GET  /health                                 -> { status }
- GET  /modules                                -> list discovered modules
- POST /select { module: <id|python.path> }    -> select module (builtin or dynamic)
- GET  /options                                -> list options of current module
- POST /set { option: str, value: any }        -> set option on current module
- POST /check                                  -> run module.check()
- POST /run                                    -> run module.run()
- POST /chatbot { query: str }                 -> optional chatbot answer

Environment/config: reads API keys from env or OTSploit.ini (same as standalone).
"""

import json
import os
import sys
import traceback
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

# Reuse logic from the standalone entry to avoid duplicating internals
# We import the file as a module and reference helpers/classes.

# Ensure cwd is project root when launched from IDEs
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import configparser  # noqa: E402
from OTSploit_standalone import (  # noqa: E402
    OTSploitException,
    S7PLCControl,
    ModbusClient,
    S7Client,
    _discover_module_paths,
    _load_module_info,
    print_info,
    print_success,
    print_error,
    print_status,
    tabulate,  # indirectly used in show; fine if imported
    _chatbot_handle_query,
)

import importlib  # noqa: E402

# Global state for the MCP server (single-user/session)
CURRENT_MODULE = None
CURRENT_MODULE_NAME = None
DISCOVERED = None
API_KEYS = None


def initialize_environment():
    global DISCOVERED, API_KEYS
    # Config
    cfg = configparser.ConfigParser(allow_no_value=True)
    try:
        cfg.read(os.path.join(PROJECT_ROOT, "OTSploit.ini"))
    except Exception:
        pass
    API_KEYS = {
        'gemini_key': os.getenv('GEMINI_API_KEY') or cfg.get('API', 'gemini_key', fallback=''),
        'serper_key': os.getenv('SERPER_API_KEY') or cfg.get('API', 'serper_key', fallback=''),
        'nvd_key': os.getenv('NVD_API_KEY') or cfg.get('API', 'nvd_key', fallback=''),
    }
    DISCOVERED = _discover_module_paths()


def module_to_info_row(idx, identifier, name, desc, kind, ok):
    return {
        "index": idx,
        "id": identifier,
        "name": name,
        "description": desc,
        "type": kind,
        "ok": bool(ok),
    }


def list_modules_json():
    rows = []
    # builtins
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
        rows.append(module_to_info_row(idx, m[0], m[1], m[2], m[3], m[4]))
        idx += 1
    # discovered
    for py_mod, kind in (DISCOVERED or []):
        name, desc, ok = _load_module_info(py_mod)
        rows.append(module_to_info_row(idx, py_mod, name, desc, kind, ok))
        idx += 1
    return rows


def select_module(identifier: str):
    global CURRENT_MODULE, CURRENT_MODULE_NAME
    # numeric?
    try:
        n = int(identifier)
        builtins_count = 3
        if n <= 0:
            raise ValueError
        if n <= builtins_count:
            identifier = ["s7_control", "modbus_client", "s7_client"][n-1]
        else:
            dm_index = n - builtins_count - 1
            if 0 <= dm_index < len(DISCOVERED or []):
                identifier = (DISCOVERED or [])[dm_index][0]
    except Exception:
        pass

    if identifier == "s7_control":
        CURRENT_MODULE = S7PLCControl()
        CURRENT_MODULE_NAME = "S7 Control"
        return {"selected": CURRENT_MODULE_NAME, "origin": "builtin"}
    if identifier == "modbus_client":
        CURRENT_MODULE = ModbusClient()
        CURRENT_MODULE_NAME = "Modbus Client"
        return {"selected": CURRENT_MODULE_NAME, "origin": "builtin"}
    if identifier == "s7_client":
        CURRENT_MODULE = S7Client()
        CURRENT_MODULE_NAME = "S7 Client"
        return {"selected": CURRENT_MODULE_NAME, "origin": "builtin"}
    if identifier == "s7_scan":
        try:
            mod = importlib.import_module('OTSploit.modules.scanners.s7comm_scan')
            ExploitClass = getattr(mod, 'Exploit', None)
            if ExploitClass is None:
                raise OTSploitException('Exploit class not found in s7comm_scan')
            CURRENT_MODULE = ExploitClass()
            CURRENT_MODULE_NAME = "S7comm Scanner"
            return {"selected": CURRENT_MODULE_NAME, "origin": 'OTSploit.modules.scanners.s7comm_scan'}
        except Exception as e:
            raise OTSploitException(f"S7comm scanner not available: {e}")
    if identifier == "profinet_scan":
        try:
            mod = importlib.import_module('OTSploit.modules.scanners.profinet_dcp_scan')
            ExploitClass = getattr(mod, 'Exploit', None)
            if ExploitClass is None:
                raise OTSploitException('Exploit class not found in profinet_dcp_scan')
            CURRENT_MODULE = ExploitClass()
            CURRENT_MODULE_NAME = "Profinet DCP Scanner"
            return {"selected": CURRENT_MODULE_NAME, "origin": 'OTSploit.modules.scanners.profinet_dcp_scan'}
        except Exception as e:
            raise OTSploitException(f"Profinet DCP scanner not available: {e}")
    if identifier == "enip_scan":
        try:
            mod = importlib.import_module('OTSploit.modules.scanners.enip_scan')
            ExploitClass = getattr(mod, 'Exploit', None)
            if ExploitClass is None:
                raise OTSploitException('Exploit class not found in enip_scan')
            CURRENT_MODULE = ExploitClass()
            CURRENT_MODULE_NAME = "ENIP Scanner"
            return {"selected": CURRENT_MODULE_NAME, "origin": 'OTSploit.modules.scanners.enip_scan'}
        except Exception as e:
            raise OTSploitException(f"ENIP scanner not available: {e}")

    if identifier.startswith('OTSploit.modules.'):
        try:
            mod = importlib.import_module(identifier)
            ExploitClass = getattr(mod, 'Exploit', None)
            if ExploitClass is None:
                raise OTSploitException('Exploit class not found in module')
            CURRENT_MODULE = ExploitClass()
            info_dict = getattr(ExploitClass, f"_{ExploitClass.__name__}__info__", {})
            CURRENT_MODULE_NAME = info_dict.get('name') or identifier.split('.')[-1]
            return {"selected": CURRENT_MODULE_NAME, "origin": identifier}
        except Exception as e:
            raise OTSploitException(f"Failed to load module: {identifier}: {e}")

    raise OTSploitException(f"Unknown module: {identifier}")


def current_options():
    m = CURRENT_MODULE
    if not m:
        return []
    rows = []
    attrs = getattr(m, 'exploit_attributes', {}) or {}
    if attrs:
        for key, desc in attrs.items():
            try:
                val = getattr(m, key)
            except Exception:
                val = ''
            rows.append({"option": key, "value": val, "description": desc})
    else:
        for key in dir(m):
            if key.startswith('_'):
                continue
            if callable(getattr(m, key)):
                continue
            try:
                val = getattr(m, key)
            except Exception:
                continue
            if isinstance(val, (str, int)):
                rows.append({"option": key, "value": val, "description": ""})
    return rows


def set_option(option: str, value):
    m = CURRENT_MODULE
    if not m:
        raise OTSploitException("No module selected")

    def coerce(opt_name, val):
        try:
            if opt_name in [
                "port", "slot", "rack", "command", "timeout", "threads", "verbose",
                "min_rack", "max_rack", "min_slot", "max_slot", "lport", "rport",
            ]:
                return int(val)
        except Exception:
            pass
        return val

    alias_map = {
        'lhost': ["lhost", "l_ip", "local_ip", "rev_ip", "callback_ip"],
        'lport': ["lport", "l_port", "local_port", "rev_port", "callback_port"],
        'rhost': ["rhost", "target", "ip", "host", "remote_ip"],
        'rport': ["rport", "port", "remote_port"],
        'target': ["target", "ip", "host", "rhost"],
    }

    # direct
    if hasattr(m, option):
        setattr(m, option, coerce(option, value))
        return {"set": option, "value": getattr(m, option)}

    # alias
    if option in alias_map:
        for candidate in alias_map[option]:
            if hasattr(m, candidate):
                setattr(m, candidate, coerce(candidate, value))
                return {"set": candidate, "value": getattr(m, candidate)}

    # exploit_attributes
    attrs = getattr(m, 'exploit_attributes', {}) or {}
    if option in attrs:
        setattr(m, option, coerce(option, value))
        return {"set": option, "value": getattr(m, option)}

    raise OTSploitException(f"Unknown option: {option}")


def ensure_required_before_run():
    m = CURRENT_MODULE
    missing = []
    for required in ["target", "ip", "rhost"]:
        if hasattr(m, required):
            try:
                v = getattr(m, required)
                if v is None or (isinstance(v, str) and v.strip() == ""):
                    missing.append(required)
            except Exception:
                pass
    if missing:
        raise OTSploitException(f"Missing required options: {', '.join(missing)}")


class Handler(BaseHTTPRequestHandler):
    server_version = "OTSploitMCP/1.0"

    def _send(self, code=200, payload=None):
        body = json.dumps(payload or {}, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):  # noqa: N802
        try:
            path = urlparse(self.path).path
            if path == '/health':
                self._send(200, {"status": "ok"})
                return
            if path == '/modules':
                self._send(200, {"modules": list_modules_json()})
                return
            if path == '/options':
                self._send(200, {"module": CURRENT_MODULE_NAME, "options": current_options()})
                return
            self._send(404, {"error": "not found"})
        except Exception as e:
            self._send(500, {"error": str(e)})

    def do_POST(self):  # noqa: N802
        try:
            path = urlparse(self.path).path
            length = int(self.headers.get('Content-Length') or 0)
            raw = self.rfile.read(length) if length else b"{}"
            try:
                data = json.loads(raw.decode('utf-8') or "{}")
            except Exception:
                data = {}

            if path == '/select':
                ident = data.get('module')
                if not ident:
                    self._send(400, {"error": "module missing"})
                    return
                try:
                    result = select_module(ident)
                    self._send(200, result)
                except Exception as e:
                    self._send(400, {"error": str(e)})
                return

            if path == '/set':
                opt = data.get('option')
                val = data.get('value')
                if not opt:
                    self._send(400, {"error": "option missing"})
                    return
                try:
                    result = set_option(opt, val)
                    self._send(200, result)
                except Exception as e:
                    self._send(400, {"error": str(e)})
                return

            if path == '/check':
                if not CURRENT_MODULE:
                    self._send(400, {"error": "no module selected"})
                    return
                try:
                    print_status("Checking target...")
                    res = CURRENT_MODULE.check()
                    self._send(200, {"result": res})
                except Exception as e:
                    self._send(500, {"error": str(e)})
                return

            if path == '/run':
                if not CURRENT_MODULE:
                    self._send(400, {"error": "no module selected"})
                    return
                try:
                    ensure_required_before_run()
                    print_status("Running module...")
                    CURRENT_MODULE.run()
                    self._send(200, {"result": "ok"})
                except Exception as e:
                    self._send(500, {"error": str(e)})
                return

            if path == '/chatbot':
                q = data.get('query', '')
                if not isinstance(q, str) or not q.strip():
                    self._send(400, {"error": "query missing"})
                    return
                try:
                    ans = _chatbot_handle_query(q, API_KEYS or {}, CURRENT_MODULE)
                    self._send(200, {"answer": ans})
                except Exception as e:
                    self._send(500, {"error": str(e)})
                return

            self._send(404, {"error": "not found"})
        except Exception:
            self._send(500, {"error": "internal error", "detail": traceback.format_exc()})


def run_server(host='127.0.0.1', port=8765):
    initialize_environment()
    httpd = HTTPServer((host, port), Handler)
    print_success(f"OTSploit MCP server running on http://{host}:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print_info("Shutting down...")
    finally:
        httpd.server_close()


"""
MCP stdio server support (real MCP) using the Python mcp SDK.
Enable by running: python -S OTSploitMCP.py --mcp-stdio
This mode exposes OTSploit operations as MCP tools for Cursor.
"""

def _run_mcp_stdio():
    try:
        # Lazy import so HTTP mode works without SDK
        from mcp.server.fastmcp import FastMCP
        from mcp.server.stdio import stdio_server
    except Exception as _e:  # noqa: N816
        print_error("MCP SDK not installed. Install with: pip install mcp")
        raise

    initialize_environment()

    server = FastMCP("otsploit")

    @server.tool()
    def health() -> dict:
        return {"status": "ok"}

    @server.tool()
    def list_modules() -> dict:
        return {"modules": list_modules_json()}

    @server.tool()
    def select(module: str) -> dict:
        return select_module(module)

    @server.tool()
    def options() -> dict:
        return {"module": CURRENT_MODULE_NAME, "options": current_options()}

    @server.tool()
    def set(option: str, value: str) -> dict:
        return set_option(option, value)

    @server.tool()
    def check() -> dict:
        if not CURRENT_MODULE:
            return {"error": "no module selected"}
        res = CURRENT_MODULE.check()
        return {"result": res}

    @server.tool()
    def run() -> dict:
        if not CURRENT_MODULE:
            return {"error": "no module selected"}
        ensure_required_before_run()
        CURRENT_MODULE.run()
        return {"result": "ok"}

    @server.tool()
    def chatbot(query: str) -> dict:
        ans = _chatbot_handle_query(query, API_KEYS or {}, CURRENT_MODULE)
        return {"answer": ans}

    with stdio_server() as (read, write):
        server.run(read, write)


if __name__ == '__main__':
    # If '--mcp-stdio' is present, run real MCP server over stdio
    if any(arg == '--mcp-stdio' for arg in sys.argv[1:]):
        _run_mcp_stdio()
    else:
        # Default: run lightweight HTTP REST bridge
        p = int(os.getenv('OTSPLOIT_MCP_PORT', '8765'))
        h = os.getenv('OTSPLOIT_MCP_HOST', '127.0.0.1')
        run_server(h, p)
