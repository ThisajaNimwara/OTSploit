# Troubleshooting

## Missing packages when using `-S`
Error: `ModuleNotFoundError: No module named 'termcolor'`.

Fix: install into the interpreter used for `-S`:
```bash
python -m pip install termcolor tabulate requests
```
Or run without `-S`:
```bash
python OTSploit_standalone.py
```

## Import error in module list (Status: ERR)
Some modules require protocol shims or OS capabilities. Ensure dependencies are installed and try running with elevated privileges.

## No results from scanners
- Use correct NIC (e.g., set `nic` option)
- Increase timeouts
- Run as admin/root

## Raw sockets/Scapy issues on Windows
- Run PowerShell as Administrator
- Ensure WinPcap/Npcap installed (if required by Scapy)

## Network reachability
- Verify target IP, port, rack/slot
- Check firewalls, VLANs, and routing
