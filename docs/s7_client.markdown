# S7comm Client

This guide demonstrates how to use the S7comm Client in OTSploit to interact with Siemens S7 PLCs.

## Initializing the Client

Create and connect to an S7 PLC:

```python
>>> from icssploit.clients.s7_client import S7Client
>>> target = S7Client(name="test", ip="192.168.1.10", rack=0, slot=3)
>>> target.connect()
```

## Getting Target Information

Retrieve PLC details:

```python
>>> order_code, version, module_type_name, as_name, module_name, serial_number = target.get_target_info()
>>> print(order_code)
6ES7 412-2EK06-0AB0
>>> print(version)
V 6.0.3
>>> print(module_type_name)
CPU 412-2 PN/DP
>>> print(as_name)
S7-400 station_1
>>> print(module_name)
PLC_1
>>> print(serial_number)
SVPF126xxxx
```

## Getting Target CPU Status

Check the CPU status:

```python
>>> target.get_target_status()
[INFO] [s7_client.get_target_status] Target is in stop mode
```

## Starting the Target CPU

Start the PLC (use `cold=True` for a cold restart):

```python
>>> target.start_target()
[INFO] [s7_client.get_target_status] Target is in stop mode
[INFO] [s7_client.start_target] Trying to start target
[INFO] [s7_client.get_target_status] Target is in run mode
>>> target.get_target_status()
[INFO] [s7_client.get_target_status] Target is in run mode
```

## Stopping the Target CPU

Stop the PLC:

```python
>>> target.stop_target()
[INFO] [s7_client.get_target_status] Target is in run mode
[INFO] [s7_client.stop_target] Trying to stop target
[INFO] [s7_client.get_target_status] Target is in stop mode
>>> target.get_target_status()
[INFO] [s7_client.get_target_status] Target is in stop mode
```

## Checking CPU Protection Level

Verify the PLC's protection level:

```python
>>> target.check_privilege()
[INFO] [s7_client._get_cpu_protect_level] CPU protect level is 1
[INFO] [s7_client.check_privilege] You have full privilege with this target
```

If the PLC has read-only protection:

```python
>>> target.check_privilege()
[INFO] [s7_client._get_cpu_protect_level] CPU protect level is 2
[INFO] [s7_client.check_privilege] You only have read privilege with this target
```

## Authenticating a Session

Authenticate with a password:

```python
>>> target.check_privilege()
[INFO] [s7_client._get_cpu_protect_level] CPU protect level is 2
[INFO] [s7_client.check_privilege] You only have read privilege with this target

# Authenticate with incorrect password
>>> target.auth("2")
[INFO] [s7_client.auth] Start authentication with password 2
[ERROR] [s7_client.auth] Got error code: Incorrect password entered (0xd602)
[ERROR] [s7_client.auth] Authentication failure
[INFO] [s7_client._get_cpu_protect_level] CPU protect level is 2
[INFO] [s7_client.check_privilege] You only have read privilege with this target

# Authenticate with correct password
>>> target.auth("1")
[INFO] [s7_client.auth] Start authentication with password 1
[INFO] [s7_client.auth] Authentication succeeded
[INFO] [s7_client._get_cpu_protect_level] CPU protect level is 2
[INFO] [s7_client.check_privilege] You have full privilege with this target
```

## Uploading a Block from the Target

Upload an OB1 block:

```python
>>> block_data = target.upload_block_from_target(block_type='OB', block_num=1)
[INFO] [s7_client.upload_block_from_target] Start uploading OB1 from target
[INFO] [s7_client.upload_block_from_target] Uploaded OB1 from target successfully
>>> print(block_data)
b'pp\x01\x01\x02\x08\x00\x01\x00\x00\x00\xb4\x00...\x00\x00\x00'
```

## Downloading a Block to the Target

Download an OB1 block (example data):

```python
>>> block_data = b'pp\x01\x01\x02\x08\x00\x01\x00\x00\x00\xb4\x00...\x00\x00\x00'
>>> target.download_block_to_target(block_data)
[INFO] [s7_client.download_block_to_target] Start downloading OB1 to target
[INFO] [s7_client.download_block_to_target] Downloaded OB1 to target successfully
```

## Reading and Writing Variables

### Supported Area Types

The `area_type` parameter specifies the memory area to access:

```python
{
    'P': 0x80,      # I/O
    'I': 0x81,      # Memory area of inputs
    'Q': 0x82,      # Memory area of outputs
    'M': 0x83,      # Memory area of bit memory
    'DB': 0x84,     # Data block
    'L': 0x86,      # Local data
    'V': 0x87       # Previous local data
}
```

### Supported Data Types

The `data_type` parameter specifies the data type to read or write:

```python
{
    0x00: "Null (0x00)",
    # 1-byte types
    0x01: "BIT (0x01)",
    0x02: "BYTE (0x02)",
    0x03: "CHAR (0x03)",
    # 2-byte types
    0x04: "WORD (0x04)",
    0x05: "INT (0x05)",
    # 4-byte types
    0x06: "DWORD (0x06)",
    0x07: "DINT (0x07)",
    0x08: "REAL (0x08)",
    # Special types
    0x09: "Str (0x09)",
    0x0a: "TOD (0x0a)",
    0x0b: "TIME (0x0b)",
    0x0c: "S5TIME (0x0c)",
    0x0f: "DATE_AND_TIME (0x0f)",
    0x1c: "COUNTER (0x1c)",
    0x1d: "TIMER (0x1d)",
    0x1e: "IEC TIMER (0x1e)",
    0x1f: "IEC COUNTER (0x1f)",
    0x20: "HS COUNTER (0x20)"
}
```

### Reading Variables

The `read_var` method takes a list of tuples containing `(area_type, address, data_type, count)`. The `address` can be specified as `"BYTE.BIT"` (e.g., `"1.0"`) or as a bit offset (e.g., `8`).

Examples:

```python
# Read 1 bit from M zone at address 1.0
>>> read_items = [("M", "1.0", "bit", 1)]
>>> target.read_var(read_items)
[1]

# Read 3 bytes from DB1 at address 2
>>> read_items = [("DB1", "2.0", "byte", 3)]
>>> target.read_var(read_items)
[[10, 20, 30]]

# Read 2 words from M zone at address 10
>>> read_items = [("M", "10.0", "word", 2)]
>>> target.read_var(read_items)
[[1, 2]]

# Read 2 reals from M zone at address 20
>>> read_items = [("M", "20.0", "real", 2)]
>>> target.read_var(read_items)
[[0.10000000149011612, 1.100000023841858]]

# Read 2 integers from M zone at address 30
>>> read_items = [("M", "30.0", "int", 2)]
>>> target.read_var(read_items)
[[100, -100]]

# Read multiple variables
>>> read_items = [("M", "1.0", "bit", 1), ("DB1", "2.0", "byte", 3), ("M", "10.0", "word", 2), ("M", "30.0", "int", 2)]
>>> target.read_var(read_items)
[1, [10, 20, 30], [1, 2], [100, -100]]
```

### Writing Variables

The `write_var` method takes a list of tuples containing `(area_type, address, data_type, data)`. The `data` must match the specified `data_type`. A return code of `255` indicates success.

Examples:

```python
# Write 1 bit to M zone at address 1.0
>>> write_items = [("M", "1.0", "bit", [1])]
>>> target.write_var(write_items)
[255]

# Write 3 bytes to DB1 at address 2
>>> write_items = [("DB1", "2.0", "byte", [10, 20, 30])]
>>> target.write_var(write_items)
[255]

# Write 2 words to M zone at address 10
>>> write_items = [("M", "10.0", "word", [1, 2])]
>>> target.write_var(write_items)
[255]

# Write 2 reals to M zone at address 20
>>> write_items = [("M", "20.0", "real", [0.1, 1.1])]
>>> target.write_var(write_items)
[255]

# Write 2 integers to M zone at address 30
>>> write_items = [("M", "30.0", "int", [100, -100])]
>>> target.write_var(write_items)
[255]

# Write multiple variables
>>> write_items = [("M", "1.0", "bit", [1]), ("DB1", "2.0", "byte", [10, 20, 30]), ("M", "10.0", "word", [1, 2])]
>>> target.write_var(write_items)
[255, 255, 255]
```

## Notes

- Ensure the target PLC is reachable on port 102/TCP and supports the S7comm protocol.
- Use `try-except` blocks in scripts to handle connection or authentication errors.
- For protected PLCs, authenticate with the correct password before performing write operations.
- The `upload_block_from_target` and `download_block_to_target` methods require valid block data.

## Troubleshooting

- **Connection Errors**: Verify the IP, rack, and slot settings. Ensure port 102 is open.
- **Authentication Failures**: Double-check the password and PLC protection level.
- **Scapy Issues**: Install `scapy` manually as per the [official guide](https://scapy.readthedocs.io/en/latest/installation.html).
- **Permission Errors**: Run OTSploit with `sudo` if required for network access.