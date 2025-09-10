#!/usr/bin/env python3
"""
Isolated test to identify the MODULES_DIR issue.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

print("Testing isolated imports...")

try:
    print("1. Testing basic Python imports...")
    import os
    import sys
    print("✓ Basic imports work")
except Exception as e:
    print(f"✗ Basic imports failed: {e}")
    sys.exit(1)

try:
    print("2. Testing termcolor import...")
    from termcolor import colored
    print("✓ termcolor import works")
except Exception as e:
    print(f"✗ termcolor import failed: {e}")
    sys.exit(1)

try:
    print("3. Testing tabulate import...")
    from tabulate import tabulate
    print("✓ tabulate import works")
except Exception as e:
    print(f"✗ tabulate import failed: {e}")
    sys.exit(1)

try:
    print("4. Testing OTSploit package import...")
    import OTSploit
    print("✓ OTSploit package import works")
except Exception as e:
    print(f"✗ OTSploit package import failed: {e}")
    sys.exit(1)

try:
    print("5. Testing OTSploit.utils import...")
    import OTSploit.utils
    print("✓ OTSploit.utils import works")
    print(f"   Available attributes: {[attr for attr in dir(OTSploit.utils) if not attr.startswith('_')]}")
except Exception as e:
    print(f"✗ OTSploit.utils import failed: {e}")
    sys.exit(1)

try:
    print("6. Testing specific utils functions...")
    from OTSploit.utils import print_info, print_success, print_error, print_status
    print("✓ Utils functions import works")
except Exception as e:
    print(f"✗ Utils functions import failed: {e}")
    sys.exit(1)

print("\n✅ All isolated tests passed!")
print("The issue might be in the interpreter or exploits modules.")
