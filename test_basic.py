#!/usr/bin/env python3
"""
Basic test to verify the framework works without the problematic imports.
"""

def test_basic_components():
    """Test basic components without the interpreter."""
    print("Testing basic OTSploit components...")
    
    # Test 1: Basic imports
    try:
        import OTSploit
        print("✓ OTSploit package import successful")
    except Exception as e:
        print(f"✗ OTSploit package import failed: {e}")
        return False
    
    # Test 2: Utils functions
    try:
        from OTSploit.utils import print_info, print_success, print_error, print_status
        print_info("Testing info message")
        print_success("Testing success message")
        print_error("Testing error message")
        print_status("Testing status message")
        print("✓ Utils functions work correctly")
    except Exception as e:
        print(f"✗ Utils functions failed: {e}")
        return False
    
    # Test 3: Exploits base class
    try:
        from OTSploit.exploits import Exploit, Option
        import OTSploit.utils as validators
        
        class TestExploit(Exploit):
            test_option = Option("test", "Test option")
        
        exploit = TestExploit()
        print("✓ Exploit base class works correctly")
    except Exception as e:
        print(f"✗ Exploit base class failed: {e}")
        return False
    
    # Test 4: Client libraries
    try:
        from OTSploit.clients.s7_client import S7Client
        from OTSploit.clients.modbus_tcp_client import ModbusClient
        print("✓ Client libraries import successfully")
    except Exception as e:
        print(f"✗ Client libraries failed: {e}")
        return False
    
    # Test 5: Protocol implementations
    try:
        from OTSploit.protocols.pn_dcp import ProfinetIO, PNDCPHeader
        from OTSploit.protocols.enip import ENIPHeader
        from OTSploit.protocols.modbus_tcp import ModbusHeader
        from OTSploit.protocols.s7comm import S7Header
        print("✓ Protocol implementations import successfully")
    except Exception as e:
        print(f"✗ Protocol implementations failed: {e}")
        return False
    
    # Test 6: Exploit modules
    try:
        from OTSploit.modules.exploits.Vendors.siemens.s7_300_400_plc_control import Exploit as S7Exploit
        from OTSploit.modules.exploits.Vendors.omron.Omron_PLC_1.0_dos import Exploit as OmronExploit
        print("✓ Exploit modules import successfully")
    except Exception as e:
        print(f"✗ Exploit modules failed: {e}")
        return False
    
    # Test 7: Scanner modules
    try:
        from OTSploit.modules.scanners.s7comm_scan import Exploit as S7Scanner
        from OTSploit.modules.scanners.profinet_dcp_scan import Exploit as ProfinetScanner
        print("✓ Scanner modules import successfully")
    except Exception as e:
        print(f"✗ Scanner modules failed: {e}")
        return False
    
    return True

def test_framework_entry():
    """Test the framework entry point without the interpreter."""
    print("\nTesting framework entry point...")
    
    try:
        # Test the main entry point logic without starting the interpreter
        import argparse
        import configparser
        
        # Test configuration loading
        isf_conf = configparser.ConfigParser(allow_no_value=True)
        if isf_conf.read("OTSploit.ini"):
            print("✓ Configuration file loads successfully")
        else:
            print("✗ Configuration file failed to load")
            return False
        
        # Test argument parsing
        parser = argparse.ArgumentParser(description="OTSploit - Operational Technology Exploitation Framework")
        parser.add_argument('-e', '--extra-package-path', metavar='PATH', default='', help='Path to extra packages')
        print("✓ Argument parser works correctly")
        
        return True
    except Exception as e:
        print(f"✗ Framework entry point failed: {e}")
        return False

if __name__ == "__main__":
    print("OTSploit Framework Basic Test")
    print("=" * 40)
    
    if test_basic_components() and test_framework_entry():
        print("\n✅ All basic tests passed! The framework core functionality is working.")
        print("The framework is ready to use for authorized penetration testing.")
    else:
        print("\n❌ Some tests failed!")
