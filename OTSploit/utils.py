#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import collections.abc
import itertools
from termcolor import colored
from tabulate import tabulate
import re

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

def pprint_dict_in_order(dictionary, order=()):
    """Pretty print dictionary in specified order."""
    for key in order:
        if key in dictionary:
            print_info(f"{key}: {dictionary[key]}")
    for key, value in sorted(dictionary.items()):
        if key not in order:
            print_info(f"{key}: {value}")

def print_table(headers, *args, **kwargs):
    """Print data in a table format."""
    table = []
    for item in args:
        table.append(item)
    print(tabulate(table, headers=headers, tablefmt='grid'), **kwargs)

def pythonize_path(path):
    """Convert human-readable path to Python module path."""
    return path.replace('/', '.').replace('\\', '.')

def humanize_path(path):
    """Convert Python module path to human-readable path."""
    return path.replace('.', os.sep)

def index_modules(modules_directory='OTSploit/modules'):
    """Index modules in the main modules directory."""
    modules = []
    for root, _, files in os.walk(modules_directory):
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                module_path = os.path.join(root, file)
                module_path = module_path[len(modules_directory) + 1:-3]
                module_path = pythonize_path(module_path)
                modules.append(module_path)
    return sorted(modules)

def index_extra_modules(modules_directory):
    """Index extra modules in the specified directory."""
    modules = []
    for root, _, files in os.walk(modules_directory):
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                module_path = os.path.join(root, file)
                module_path = module_path[len(modules_directory) + 1:-3]
                module_path = f"extra_exploits.{pythonize_path(module_path)}"
                modules.append(module_path)
    return sorted(modules)

def import_exploit(module_path):
    """Dynamically import an exploit module."""
    try:
        module = __import__(module_path, fromlist=['Exploit'])
        return getattr(module, 'Exploit')
    except ImportError as e:
        raise OTSploitException(f"Failed to import module {module_path}: {str(e)}")

class NonStringIterable:
    """Check if an object is iterable but not a string."""
    def __instancecheck__(self, instance):
        return isinstance(instance, collections.abc.Iterable) and not isinstance(instance, (str, bytes))

def stop_after(max_suggestions):
    """Decorator to limit tab completion suggestions."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            return result[:max_suggestions]
        return wrapper
    return decorator

def module_required(func):
    """Decorator to ensure a module is selected."""
    def wrapper(self, *args, **kwargs):
        if not self.current_module:
            raise OTSploitException("No module selected. Please use a module first.")
        return func(self, *args, **kwargs)
    return wrapper

# Validators
def ipv4(value):
    """Validate IPv4 address."""
    parts = str(value).split('.')
    if len(parts) != 4:
        raise ValueError("Invalid IPv4 address: must have 4 octets")
    for part in parts:
        try:
            num = int(part)
            if num < 0 or num > 255:
                raise ValueError
        except ValueError:
            raise ValueError(f"Invalid IPv4 address: {value}")
    return value

def url(value):
    """Validate URL."""
    regex = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    if not regex.match(str(value)):
        raise ValueError(f"Invalid URL: {value}")
    return value

def integer(value):
    """Validate integer."""
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"Invalid integer: {value}")

def ipv4_or_url(value):
    """Validate either an IPv4 address or a URL."""
    try:
        return ipv4(value)
    except ValueError:
        return url(value)

def string(value):
    """Validate string."""
    return str(value)

def port_scan(protocol='TCP', target='127.0.0.1', port=80):
    """Perform port scan using nmap."""
    import nmap
    nm = nmap.PortScanner()
    nm.scan(target, str(port), arguments='-sS')
    return nm

def export_table(file_path, headers, data):
    """Export table data to CSV file."""
    import csv
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        writer.writerows(data)
    print_info(f"Table exported to {file_path}")

def mute(func):
    """Decorator to suppress output during check operations."""
    def wrapper(*args, **kwargs):
        import sys
        from io import StringIO
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            sys.stdout = old_stdout
    return wrapper
