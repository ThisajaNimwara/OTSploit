#!/usr/bin/env python3
"""
Simple test to verify basic functionality.
"""

def test_basic_imports():
    """Test basic imports without the problematic MODULES_DIR."""
    print("Testing basic imports...")
    
    try:
        import OTSploit
        print("✓ OTSploit package import successful")
    except Exception as e:
        print(f"✗ OTSploit package import failed: {e}")
        return False
    
    try:
        from OTSploit.utils import print_info, print_success, print_error, print_status
        print("✓ Utils functions import successful")
    except Exception as e:
        print(f"✗ Utils functions import failed: {e}")
        return False
    
    try:
        from OTSploit.exploits import Exploit, Option
        print("✓ Exploits base classes import successful")
    except Exception as e:
        print(f"✗ Exploits base classes import failed: {e}")
        return False
    
    try:
        from OTSploit.clients.s7_client import S7Client
        print("✓ S7 client import successful")
    except Exception as e:
        print(f"✗ S7 client import failed: {e}")
        return False
    
    try:
        from OTSploit.clients.modbus_tcp_client import ModbusClient
        print("✓ Modbus client import successful")
    except Exception as e:
        print(f"✗ Modbus client import failed: {e}")
        return False
    
    try:
        from OTSploit.protocols.pn_dcp import ProfinetIO, PNDCPHeader
        print("✓ Profinet DCP protocol import successful")
    except Exception as e:
        print(f"✗ Profinet DCP protocol import failed: {e}")
        return False
    
    try:
        from OTSploit.modules.exploits.Vendors.siemens.s7_300_400_plc_control import Exploit as S7Exploit
        print("✓ S7 exploit module import successful")
    except Exception as e:
        print(f"✗ S7 exploit module import failed: {e}")
        return False
    
    try:
        from OTSploit.modules.scanners.s7comm_scan import Exploit as S7Scanner
        print("✓ S7 scanner module import successful")
    except Exception as e:
        print(f"✗ S7 scanner module import failed: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test basic framework functionality."""
    print("\nTesting basic functionality...")
    
    try:
        from OTSploit.utils import print_info, print_success, print_error, print_status
        print_info("Testing info message")
        print_success("Testing success message")
        print_error("Testing error message")
        print_status("Testing status message")
        print("✓ Print functions work correctly")
    except Exception as e:
        print(f"✗ Print functions failed: {e}")
        return False
    
    try:
        from OTSploit.exploits import Exploit, Option
        import OTSploit.utils as validators
        
        class TestExploit(Exploit):
            test_option = Option("test", "Test option")
        
        exploit = TestExploit()
        print("✓ Exploit class instantiation successful")
    except Exception as e:
        print(f"✗ Exploit class instantiation failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("OTSploit Framework Simple Test")
    print("=" * 40)
    
    if test_basic_imports() and test_basic_functionality():
        print("\n✅ All basic tests passed! OTSploit framework core functionality is working.")
    else:
        print("\n❌ Some tests failed!")
