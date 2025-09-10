# Modbus-TCP Client

This guide demonstrates how to use the Modbus-TCP Client in OTSploit to interact with Modbus-TCP devices.

## Initializing the Client

Create and connect to a Modbus-TCP device:

```python
>>> from icssploit.clients.modbus_tcp_client import ModbusClient
>>> target = ModbusClient(name='modbus_tcp_client', ip="172.16.99.133")
>>> target.connect()
```

## Reading Coils

Read 10 coils starting at address 100:

```python
>>> target.read_coils(address=100, count=10)
[*] Sending Modbus read coils request...
['0', '0', '0', '0', '0', '0', '0', '0', '0', '0']
```

## Writing Coils

Write multiple coils starting at address 100:

```python
>>> target.write_multiple_coils(address=100, values=[0, 0, 0, 0, 1, 1, 1, 1])
[*] Sending Modbus write coils request...
<ModbusHeaderResponse trans_id=3 proto_id=0 length=6 unit_id=0 func_code=15 |<WriteMultipleCoilsResponse ReferenceNumber=100 BitCount=8 |>>
>>> target.read_coils(address=100, count=8)
[*] Sending Modbus read coils request...
['0', '0', '0', '0', '1', '1', '1', '1']
```

## Reading Holding Registers

Read 10 holding registers starting at address 100:

```python
>>> target.read_holding_registers(address=100, count=10)
[*] Sending Modbus read holding registers request...
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
```

## Writing Registers

Write multiple registers starting at address 100:

```python
>>> target.write_multiple_registers(address=100, values=[0x01, 0x02, 0x03, 0x04])
[*] Sending Modbus write registers request...
<ModbusHeaderResponse trans_id=3 proto_id=0 length=6 unit_id=0 func_code=16 |<WriteMultipleRegistersResponse ReferenceNumber=100 WordCount=4 |>>
>>> target.read_holding_registers(address=100, count=4)
[*] Sending Modbus read holding registers request...
[1, 2, 3, 4]
```

## Reading Input Registers

Read 10 input registers starting at address 100:

```python
>>> target.read_input_registers(address=100, count=10)
[*] Sending Modbus read input registers request...
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
```

## Notes

- Ensure the target device is reachable and supports Modbus-TCP on the specified IP and port (default: 502).
- Use `try-except` blocks in scripts to handle connection errors gracefully.
- The client uses `scapy` for packet crafting, so ensure it is installed correctly.

## Troubleshooting

- **Connection Errors**: Verify the target IP and network connectivity. Ensure no firewall blocks port 502.
- **Scapy Issues**: Install `scapy` manually as per the [official guide](https://scapy.readthedocs.io/en/latest/installation.html).
- **No Response**: Increase timeout values in the client configuration or check if the device is online.