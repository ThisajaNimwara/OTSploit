#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function
import argparse
import logging.handlers
import os
import configparser
from OTSploit.interpreter import OTsploitInterpreter

# Initialize configuration
isf_conf_file = "OTSploit.ini"
isf_conf = configparser.ConfigParser(allow_no_value=True)

# Load configuration file with error handling
try:
    if not isf_conf.read(isf_conf_file):
        raise FileNotFoundError(f"Configuration file '{isf_conf_file}' not found or unreadable.")
except Exception as e:
    print(f"Error loading configuration: {e}")
    exit(1)

# Get parameters from configuration with defaults
try:
    log_file_name = isf_conf.get("LOG", "log_file_name", fallback="otsploit.log")
    log_max_bytes = isf_conf.getint("LOG", "log_max_bytes", fallback=10485760)  # 10MB default
    log_level = isf_conf.getint("LOG", "log_level", fallback=logging.INFO)
    package_path = isf_conf.get("EXTRA_PACKAGE", "package_path", fallback="extra_packages")
except configparser.Error as e:
    print(f"Error reading configuration: {e}")
    exit(1)

# Configure logging
log_handler = logging.handlers.RotatingFileHandler(
    filename=log_file_name,
    maxBytes=log_max_bytes,
    backupCount=5
)
log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s       %(message)s')
log_handler.setFormatter(log_formatter)
logger = logging.getLogger()
logger.setLevel(log_level)
logger.addHandler(log_handler)

# Argument parsing
parser = argparse.ArgumentParser(
    description="OTSploit - Operational Technology Exploitation Framework",
    epilog="Example: python3 OTSploit.py -e /path/to/extra/packages"
)
parser.add_argument(
    '-e', '--extra-package-path',
    metavar='PATH',
    default=package_path,
    help='Path to extra packages (clients, modules, protocols) for OTSploit.'
)

def icssploit(extra_package_path):
    """Start the OTSploit interpreter with the specified package path."""
    if extra_package_path and not os.path.isdir(extra_package_path):
        logger.error(f"Extra package path '{extra_package_path}' is not a valid directory.")
        print(f"Error: '{extra_package_path}' is not a valid directory.")
        return
    try:
        isf = OTsploitInterpreter(extra_package_path)
        isf.start()
    except Exception as e:
        logger.critical(f"Failed to start OTSploit interpreter: {e}")
        print(f"Error starting OTSploit: {e}")
        exit(1)

if __name__ == "__main__":
    args = parser.parse_args()
    icssploit(args.extra_package_path)