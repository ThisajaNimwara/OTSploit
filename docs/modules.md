# Modules and Options

## Listing modules
```text
OTSploit > list
```
The table shows: index, id/path, name, description, type, and status (OK/ERR).

## Selecting a module
```text
OTSploit > use 14
# or
OTSploit > use OTSploit.modules.exploits.Vendors.siemens.s7_300_400_plc_control
```

## Viewing and setting options
```text
OTSploit (Module) > show options
OTSploit (Module) > set target 192.168.1.10
OTSploit (Module) > set port 102
OTSploit (Module) > run
```

### Aliases supported
- target: target | ip | host | rhost
- rport: rport | port | remote_port
- lhost: lhost | l_ip | local_ip | rev_ip | callback_ip
- lport: lport | l_port | local_port | rev_port | callback_port

Integer-like values are auto-coerced where appropriate (e.g., port, slot, rack).

## Check mode
If a module implements `check()`, you can run:
```text
OTSploit (Module) > check
```

## Notes
- Some modules may report `Import error` in the list if dependencies or protocol packs are missing.
- For network operations or raw sockets you may need administrator/root privileges.
