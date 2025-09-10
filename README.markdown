# OT/ICS/IIoT Exploitation Framework (OTSploit)
OTSploit is a Python-based exploitation and assessment framework for Industrial Control Systems (ICS) such as PLCs, RTUs, HMIs, and industrial switches. It includes protocol clients, scanners, and exploit modules across multiple vendors, plus a CLI-based OT/ICS assistant (chatbot).

## Disclaimer
Usage of OTSploit for attacking targets without prior mutual consent is illegal. It is the end user's responsibility to obey all applicable local, state, and federal laws. Developers assume no liability and are not responsible for any misuse or damage caused by this program.

## Quick Start
1. Install Python 3.8+
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the standalone interface (recommended):
   ```bash
   python OTSploit_standalone.py
   python -S OTSploit_standalone.py
   ```
   The `-S` flag avoids environment site-packages interference.

Common commands inside the shell:
```text
OTSploit > list
OTSploit > use 14
OTSploit (S7-300/400 PLC Control) > show options
OTSploit (...) > set target 192.168.1.10
OTSploit (...) > set port 102
OTSploit (...) > run
```

## Features Overview
- Vendor modules (Siemens, Schneider, Rockwell, Omron, Phoenix, Realwin, QNX, VxWorks, Xinje, etc.)
- Scanners (S7comm, Profinet-DCP, ENIP)
- Protocol building blocks (Scapy-based)
- CLI-based assistant (chatbot) for OT/ICS queries; integrates Gemini, Serper, NVD (optional)
- MCP integration for IDEs (Cursor) via stdio + lightweight HTTP bridge

## Running (standalone UI)
```bash
python -S OTSploit_standalone.py
```

Core commands:
- `list`: Pretty table of all modules (built-in + discovered)
- `use <index|python.path>`: Select a module
- `show options`: Show module options and current values
- `set <option> <value>`: Set options (supports aliases: target/rhost/ip, rport/port, lhost, lport)
- `run`: Execute module
- `check`: If implemented by the module, run a non-intrusive check
- `chatbot [-q "text"]`: ICS/OT assistant (interactive or one-shot)

Built-in modules visible immediately on `list`:
- `s7_control`: S7-300/400 PLC control
- `modbus_client`: Modbus-TCP client
- `s7_client`: S7comm client
- `s7_scan`: S7comm scanner (alias of `OTSploit.modules.scanners.s7comm_scan`)
- `profinet_scan`: Profinet DCP scanner (alias of `OTSploit.modules.scanners.profinet_dcp_scan`)
- `enip_scan`: Ethernet/IP scanner (alias of `OTSploit.modules.scanners.enip_scan`)

## Configuration
The framework reads `OTSploit.ini`:
```ini
[LOG]
log_file_name = otsploit.log
log_max_bytes = 10485760
log_level = 20

[EXTRA_PACKAGE]
package_path = 

[API]
gemini_key = <your google gemini key>
serper_key = <your serper key>
nvd_key = <your nvd api key>
```
Alternatively set env vars: `GEMINI_API_KEY`, `SERPER_API_KEY`, `NVD_API_KEY`.

## Installation
- Python 3.8+ is recommended
- Install requirements:
  ```bash
  pip install -r requirements.txt
  ```
  For raw packet features, ensure Scapy works on your platform (may need admin/root).

If you plan to integrate with Cursor via MCP, also ensure the MCP SDK is installed (it is listed in `requirements.txt`).

```bash
pip install mcp
```

## MCP integration (Cursor)
The project ships a real MCP stdio server inside `OTSploitMCP.py`. Configure Cursor to spawn it over stdio:

1) Create or edit `C:\Users\<you>\.cursor\mcp.json`:
```json
{
  "mcpServers": {
    "otsploit": {
      "command": "C:/Users/<you>/AppData/Local/Programs/Python/Python313/python.exe",
      "args": [
        "-S",
        "C:/Users/<you>/Desktop/Learn/Learn 3/Research/OT-Exploitation-Framework/OTSploitMCP.py",
        "--mcp-stdio"
      ],
      "env": { "PYTHONUTF8": "1" },
      "autoStart": true
    }
  }
}
```
2) Restart Cursor. In the Tools/Providers panel you should see `otsploit` with tools:
`health`, `list_modules`, `select`, `options`, `set`, `check`, `run`, `chatbot`.

### Lightweight HTTP bridge (optional)
`OTSploitMCP.py` also exposes a simple REST API if run without `--mcp-stdio`:
```bash
python -S OTSploitMCP.py
# or with env/port
OTSPLOIT_MCP_HOST=0.0.0.0 OTSPLOIT_MCP_PORT=8765 python -S OTSploitMCP.py
```

Endpoints:
- `GET /health` → `{ "status": "ok" }`
- `GET /modules` → discovered + built-in modules
- `POST /select` `{ "module": "s7_scan" }`
- `GET /options`
- `POST /set` `{ "option": "target", "value": "192.168.1.10" }`
- `POST /check`
- `POST /run`
- `POST /chatbot` `{ "query": "Scan Profinet devices?" }`

Note: the root `/` returns 404 by design; use the endpoints above.

## Classic entrypoint (optional)
The original interpreter (`OTSploit.py`) is included. The standalone is preferred for modern usage, but you can still run:
```bash
python OTSploit.py -e /path/to/extra/packages
```

## Example (standalone) workflow
```text
OTSploit > list
OTSploit > use 14
OTSploit (S7-300/400 PLC Control) > show options
OTSploit (...) > set target 192.168.1.10
OTSploit (...) > set port 102
OTSploit (...) > run
```

## Chatbot (OT/ICS assistant)
Ask targeted questions with context from the currently selected module:
```text
OTSploit > chatbot -q "CVE-2024-47135 detail"
OTSploit > use 10
OTSploit (Rockwell ...) > chatbot -q "Checklist before running this module?"
OTSploit > chatbot   # interactive mode; type 'back' to exit
```

## Documentation (selected)
- Modbus-TCP Client usage
- S7comm Client usage
- Profinet DCP Scanner usage
- S7comm PLC Scanner usage
- How to write your own module

See the `docs/` directory for more.