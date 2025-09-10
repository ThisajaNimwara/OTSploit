# Profinet DCP Scanner

This guide explains how to use the Profinet DCP Scanner module to discover devices on a Profinet network.

## Using the Profinet DCP Scanner Module

Select the scanner module:

```bash
OTSploit > use scanners/profinet_dcp_scan
OTSploit (Profinet DCP Scan) >
```

### Set Options

Display available options:

```bash
OTSploit (Profinet DCP Scan) > show options
```

Output:
```
Target options:
   Name       Current settings     Description
   ----       ----------------     -----------
   target                          Target IP address

Module options:
   Name        Current settings     Description
   ----        ----------------     -----------
   nic         eth0                 Network interface (e.g., eth0, en0)
   timeout     5                    Timeout for responses (seconds)
   verbose     0                    Scapy verbose level (0 to 2)
```

Profinet DCP is an Ethernet-based protocol, so you must specify the network interface to send and receive packets. Set the interface as follows:

```bash
OTSploit (Profinet DCP Scan) > set nic eth0
[+] {'nic': 'eth0'}
```

### Run the Scan

Execute the scan:

```bash
OTSploit (Profinet DCP Scan) > run
[*] Running module...
Device Name    Device Type    MAC Address        IP Address      Netmask        Gateway
-------------  -------------  -----------------  --------------  -------------  --------------
plcxb1d0ed     S7-400         00:1b:1b:a7:xx:xx  192.168.1.10   255.255.255.0  192.168.1.10
```

## Notes

- Ensure the specified network interface (e.g., `eth0`) is active and connected to the target network.
- The `timeout` option controls how long the scanner waits for responses. Increase it for slower networks.
- Set `verbose` to `1` or `2` for more detailed Scapy output during debugging.
- If no devices are found, verify the target IP range and network connectivity.

## Troubleshooting

- **Permission Errors**: Run OTSploit with `sudo` if the network interface requires elevated privileges.
- **No Devices Found**: Ensure the target network supports Profinet DCP and that devices are online.
- **Scapy Issues**: Install `scapy` manually as per the [official guide](https://scapy.readthedocs.io/en/latest/installation.html) if errors occur.