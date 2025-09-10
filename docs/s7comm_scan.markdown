# S7comm Scanner

This guide explains how to use the S7comm Scanner module to discover Siemens S7 PLCs on a network.

## Using the S7comm Scanner Module

Select the scanner module:

```bash
OTSploit > search scanner
scanners/profinet_dcp_scan
scanners/s7comm_scan
scanners/vxworks_6_scan
OTSploit > use scanners/s7comm_scan
OTSploit (S7comm PLC Scan) >
```

### Set Options

Display available options:

```bash
OTSploit (S7comm PLC Scan) > show options
```

Output:
```
Target options:
   Name       Current settings     Description
   ----       ----------------     -----------
   target                          Host(s) as Nmap-style string (e.g., '192.168.1.0/24')
   port       102                  S7comm port (default: 102/TCP)

Module options:
   Name         Current settings     Description
   ----         ----------------     -----------
   min_slot     2                    Minimum PLC slot number for scan (default: 2)
   min_rack     0                    Minimum PLC rack number for scan (default: 0)
   max_rack     0                    Maximum PLC rack number for scan (default: 0)
   max_slot     5                    Maximum PLC slot number for scan (default: 5)
   verbose      0                    Scapy verbose level (0 to 2)
```

Set the target network:

```bash
OTSploit (S7comm PLC Scan) > set target 192.168.1.0/24
[+] {'target': '192.168.1.0/24'}
```

### Run the Scan

Execute the scan:

```bash
OTSploit (S7comm PLC Scan) > run
[*] Running module...
[+] Host: 192.168.1.10, port: 102 is open
[*] Trying to scan 192.168.1.10 with Rack0/Slot2
[ERROR] [s7_client.send_receive_packet] Connection reset by peer
[ERROR] [s7_client.send_receive_s7_packet] Connection reset by peer
[ERROR] [s7_client.get_target_info] Can't get order code and version from target
[*] Trying to scan 192.168.1.10 with Rack0/Slot3
[*] Trying to scan 192.168.1.10 with Rack0/Slot4
[ERROR] [s7_client.send_receive_packet] Connection reset by peer
[ERROR] [s7_client.send_receive_s7_packet] Connection reset by peer
[ERROR] [s7_client.get_target_info] Can't get order code and version from target
[*] Trying to scan 192.168.1.10 with Rack0/Slot5
[ERROR] [s7_client.send_receive_packet] Connection reset by peer
[ERROR] [s7_client.send_receive_s7_packet] Connection reset by peer
[ERROR] [s7_client.get_target_info] Can't get order code and version from target
[+] Found 1 target
Order Code           Module Type Name    Firmware Version    Module Name    Serial Number    Rack/Slot    IP Address
-------------------  ------------------  ------------------  -------------  ---------------  -----------  --------------
6ES7 412-2EK06-0AB0  CPU 412-2 PN/DP     V 6.0.3                            SVPF126xxxx      0/3          192.168.1.10
```

## Notes

- The scanner uses the S7comm protocol to probe PLCs on port 102/TCP by default.
- Adjust `min_rack`, `max_rack`, `min_slot`, and `max_slot` to narrow or expand the scan scope.
- Set `verbose` to `1` or `2` for detailed Scapy output during debugging.

## Troubleshooting

- **Connection Reset Errors**: Ensure the target PLC is online and port 102 is open. Check firewall settings.
- **No Targets Found**: Verify the target IP range and ensure S7comm-compatible devices are present.
- **Scapy Issues**: Install `scapy` manually as per the [official guide](https://scapy.readthedocs.io/en/latest/installation.html).
- **Permission Errors**: Run OTSploit with `sudo` if network access requires elevated privileges.