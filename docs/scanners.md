# Scanners

## S7comm Scanner
```text
OTSploit > use OTSploit.modules.scanners.s7comm_scan
OTSploit (s7comm_scan) > show options
OTSploit (s7comm_scan) > set target 192.168.1.0/24
OTSploit (s7comm_scan) > run
```

## Profinet DCP Scanner
```text
OTSploit > use OTSploit.modules.scanners.profinet_dcp_scan
OTSploit (profinet_dcp_scan) > show options
OTSploit (profinet_dcp_scan) > set nic eth0
OTSploit (profinet_dcp_scan) > run
```

## ENIP Scanner
```text
OTSploit > use OTSploit.modules.scanners.enip_scan
OTSploit (enip_scan) > show options
OTSploit (enip_scan) > set target 192.168.1.0/24
OTSploit (enip_scan) > run
```

Notes:
- Scapy-based modules may require admin/root privileges and appropriate NIC.
- Increase timeouts or verbosity if you see no results on busy links.
