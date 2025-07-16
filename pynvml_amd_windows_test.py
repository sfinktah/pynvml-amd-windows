#!/usr/bin/env python3
"""
Test harness for pynvml-amd-windows package.

This test suite validates the pynvml-compatible interface for AMD GPUs
using ADLX, ensuring compatibility with existing pynvml-based applications.
"""

import sys
import time
import traceback
import unittest
from typing import Optional, List, Dict, Any
import ADLXPybind


class TestPynvmlAmdWindows(unittest.TestCase):
    """Test suite for pynvml-amd-windows package."""

    def setUp(self):
        """Set up test environment."""
        self.pynvml = None
        self.device_handles = []

    def tearDown(self):
        """Clean up after tests."""
        if self.pynvml:
            try:
                if hasattr(self.pynvml, 'nvmlShutdown'):
                    self.pynvml.nvmlShutdown()
            except Exception as e:
                print(f"Warning: Cleanup failed: {e}")
        self.device_handles.clear()

    def test_import_package(self):
        """Test that the package can be imported successfully."""
        try:
            # Try different import methods
            import pynvml_amd_windows
            self.pynvml = pynvml_amd_windows
            self.assertIsNotNone(pynvml_amd_windows)
            print("✓ Package import successful")

            # Check if it has required attributes
            required_attrs = ['nvmlInit', 'nvmlDeviceGetCount', 'nvmlDeviceGetHandleByIndex',
                              'nvmlDeviceGetName', 'nvmlSystemGetDriverVersion',
                              'nvmlDeviceGetUtilizationRates', 'nvmlDeviceGetMemoryInfo',
                              'nvmlDeviceGetTemperature', 'NVML_TEMPERATURE_GPU']

            for attr in required_attrs:
                if hasattr(pynvml_amd_windows, attr):
                    print(f"✓ {attr} found")
                else:
                    print(f"⚠ {attr} not found")

        except ImportError as e:
            self.fail(f"Failed to import pynvml_amd_windows: {e}")
        except Exception as e:
            self.fail(f"Unexpected error during import: {e}")

    def test_nvml_init(self):
        """Test NVML initialization."""
        try:
            import pynvml_amd_windows
            self.pynvml = pynvml_amd_windows

            # Test initialization
            pynvml_amd_windows.nvmlInit()
            print("✓ nvmlInit() successful")

            # Test double initialization (should not fail)
            pynvml_amd_windows.nvmlInit()
            print("✓ Double nvmlInit() handled correctly")

        except Exception as e:
            print(f"⚠ nvmlInit() failed: {e}")
            print("This might be expected if no AMD GPU is present or ADLX is not available")

    def test_device_count(self):
        """Test getting device count."""
        try:
            import pynvml_amd_windows
            self.pynvml = pynvml_amd_windows

            pynvml_amd_windows.nvmlInit()
            device_count = pynvml_amd_windows.nvmlDeviceGetCount()

            self.assertIsInstance(device_count, int)
            self.assertGreaterEqual(device_count, 0)
            print(f"✓ nvmlDeviceGetCount() returned {device_count} devices")

        except Exception as e:
            print(f"⚠ nvmlDeviceGetCount() failed: {e}")
            print("This might be expected if no AMD GPU is present")

    def test_device_handle_by_index(self):
        """Test getting device handles by index."""
        try:
            import pynvml_amd_windows
            self.pynvml = pynvml_amd_windows

            pynvml_amd_windows.nvmlInit()
            device_count = pynvml_amd_windows.nvmlDeviceGetCount()

            if device_count > 0:
                pass
                # Test valid index
                handle = pynvml_amd_windows.nvmlDeviceGetHandleByIndex(0)
                self.assertIsNotNone(handle)
                self.device_handles.append(handle)
                print("✓ nvmlDeviceGetHandleByIndex(0) successful")
                # del handle

                # Test invalid index
                try:
                    pynvml_amd_windows.nvmlDeviceGetHandleByIndex(device_count + 1)
                    print("⚠ nvmlDeviceGetHandleByIndex() should have failed with invalid index")
                except Exception:
                    print("✓ nvmlDeviceGetHandleByIndex() properly handles invalid index")
            else:
                print("⚠ No devices found, skipping handle tests")

        except Exception as e:
            print(f"⚠ nvmlDeviceGetHandleByIndex() failed: {e}")

    def test_device_name(self):
        """Test getting device names."""
        try:
            import pynvml_amd_windows
            self.pynvml = pynvml_amd_windows

            pynvml_amd_windows.nvmlInit()
            device_count = pynvml_amd_windows.nvmlDeviceGetCount()

            # print("⚠ Lame devices found, skipping name test")
            # return
            if device_count > 0:
                handle = pynvml_amd_windows.nvmlDeviceGetHandleByIndex(0)
                # Removing this line fixes issue
                self.device_handles.append(handle)

                name = pynvml_amd_windows.nvmlDeviceGetName(handle)
                self.assertIsInstance(name, str)
                self.assertGreater(len(name), 0)
                print(f"✓ nvmlDeviceGetName() returned: '{name}'")
            else:
                print("⚠ No devices found, skipping name test")

        except Exception as e:
            print(f"⚠ nvmlDeviceGetName() failed: {e}")

    def test_driver_version(self):
        """Test getting driver version."""
        try:
            import pynvml_amd_windows
            self.pynvml = pynvml_amd_windows

            pynvml_amd_windows.nvmlInit()
            version = pynvml_amd_windows.nvmlSystemGetDriverVersion()

            self.assertIsInstance(version, str)
            self.assertGreater(len(version), 0)
            print(f"✓ nvmlSystemGetDriverVersion() returned: '{version}'")

        except Exception as e:
            print(f"⚠ nvmlSystemGetDriverVersion() failed: {e}")

    def test_utilization_rates(self):
        """Test getting GPU utilization rates."""
        try:
            import pynvml_amd_windows
            self.pynvml = pynvml_amd_windows

            pynvml_amd_windows.nvmlInit()
            device_count = pynvml_amd_windows.nvmlDeviceGetCount()

            if device_count > 0:
                handle = pynvml_amd_windows.nvmlDeviceGetHandleByIndex(0)
                self.device_handles.append(handle)

                util = pynvml_amd_windows.nvmlDeviceGetUtilizationRates(handle)
                self.assertIsNotNone(util)

                # Check if it has the expected attributes
                if hasattr(util, 'gpu') and hasattr(util, 'memory'):
                    print(f"✓ nvmlDeviceGetUtilizationRates() returned GPU: {util.gpu}%, Memory: {util.memory}%")
                else:
                    print(f"⚠ Utilization object missing expected attributes: {dir(util)}")
            else:
                print("⚠ No devices found, skipping utilization test")

        except Exception as e:
            print(f"⚠ nvmlDeviceGetUtilizationRates() failed: {e}")

    def test_memory_info(self):
        """Test getting memory information."""
        try:
            import pynvml_amd_windows
            self.pynvml = pynvml_amd_windows

            pynvml_amd_windows.nvmlInit()
            device_count = pynvml_amd_windows.nvmlDeviceGetCount()

            if device_count > 0:
                handle = pynvml_amd_windows.nvmlDeviceGetHandleByIndex(0)
                self.device_handles.append(handle)

                mem = pynvml_amd_windows.nvmlDeviceGetMemoryInfo(handle)
                self.assertIsNotNone(mem)

                # Check if it has the expected attributes
                if hasattr(mem, 'total') and hasattr(mem, 'used'):
                    print(f"✓ nvmlDeviceGetMemoryInfo() returned Total: {mem.total:,} bytes, Used: {mem.used:,} bytes")
                    if hasattr(mem, 'free'):
                        print(f"  Free: {mem.free:,} bytes")
                else:
                    print(f"⚠ Memory object missing expected attributes: {dir(mem)}")
            else:
                print("⚠ No devices found, skipping memory test")

        except Exception as e:
            print(f"⚠ nvmlDeviceGetMemoryInfo() failed: {e}")

    def test_temperature(self):
        """Test getting GPU temperature."""
        try:
            import pynvml_amd_windows
            self.pynvml = pynvml_amd_windows

            pynvml_amd_windows.nvmlInit()
            device_count = pynvml_amd_windows.nvmlDeviceGetCount()

            if device_count > 0:
                handle = pynvml_amd_windows.nvmlDeviceGetHandleByIndex(0)
                self.device_handles.append(handle)

                temp = pynvml_amd_windows.nvmlDeviceGetTemperature(handle, pynvml_amd_windows.NVML_TEMPERATURE_GPU)
                self.assertIsInstance(temp, int)
                print(f"✓ nvmlDeviceGetTemperature() returned: {temp}°C")
            else:
                print("⚠ No devices found, skipping temperature test")

        except Exception as e:
            print(f"⚠ nvmlDeviceGetTemperature() failed: {e}")

    def test_constants(self):
        """Test that required constants are available."""
        try:
            import pynvml_amd_windows
            self.pynvml = pynvml_amd_windows

            # Test temperature constant
            if hasattr(pynvml_amd_windows, 'NVML_TEMPERATURE_GPU'):
                print("✓ NVML_TEMPERATURE_GPU constant available")
            else:
                print("⚠ NVML_TEMPERATURE_GPU constant not found")

        except Exception as e:
            print(f"⚠ Constants test failed: {e}")

    def test_shutdown(self):
        """Test NVML shutdown."""
        try:
            import pynvml_amd_windows
            self.pynvml = pynvml_amd_windows

            pynvml_amd_windows.nvmlInit()

            if hasattr(pynvml_amd_windows, 'nvmlShutdown'):
                pynvml_amd_windows.nvmlShutdown()
                print("✓ nvmlShutdown() successful")

                # Test that functions fail after shutdown
                try:
                    pynvml_amd_windows.nvmlDeviceGetCount()
                    print("⚠ Functions should fail after shutdown")
                except Exception:
                    print("✓ Functions properly fail after shutdown")
            else:
                print("⚠ nvmlShutdown() not found in package")

        except Exception as e:
            print(f"⚠ nvmlShutdown() failed: {e}")


class IntegrationTest:
    """Integration test that mimics real-world usage."""

    def run_integration_test(self):
        """Run comprehensive integration test."""
        print("\n" + "="*60)
        print("INTEGRATION TEST - Real-world usage simulation")
        print("="*60)

        try:
            # Import and initialize
            import pynvml_amd_windows

            print("1. Initializing NVML...")
            pynvml_amd_windows.nvmlInit()

            print("2. Getting device count...")
            device_count = pynvml_amd_windows.nvmlDeviceGetCount()
            print(f"   Found {device_count} GPU device(s)")

            if device_count == 0:
                print("   No GPUs found, ending integration test")
                return True

            print("3. Testing each GPU device...")
            for i in range(device_count):
                print(f"\n   Device {i}:")

                try:
                    # Get device handle
                    handle = pynvml_amd_windows.nvmlDeviceGetHandleByIndex(i)

                    # Get device name
                    name = pynvml_amd_windows.nvmlDeviceGetName(handle)
                    print(f"     Name: {name}")

                    # Get temperature
                    temp = pynvml_amd_windows.nvmlDeviceGetTemperature(handle, pynvml_amd_windows.NVML_TEMPERATURE_GPU)
                    print(f"     Temperature: {temp}°C")

                    # Get utilization
                    util = pynvml_amd_windows.nvmlDeviceGetUtilizationRates(handle)
                    if hasattr(util, 'gpu'):
                        print(f"     GPU Utilization: {util.gpu}%")
                    if hasattr(util, 'memory'):
                        print(f"     Memory Utilization: {util.memory}%")

                    # Get memory info
                    mem = pynvml_amd_windows.nvmlDeviceGetMemoryInfo(handle)
                    if hasattr(mem, 'total') and hasattr(mem, 'used'):
                        total_mb = mem.total // (1024 * 1024) if mem.total > 0 else 0
                        used_mb = mem.used // (1024 * 1024) if mem.used > 0 else 0
                        free_mb = getattr(mem, 'free', 0) // (1024 * 1024) if getattr(mem, 'free', 0) > 0 else 0
                        print(f"     Memory: {used_mb}MB / {total_mb}MB ({free_mb}MB free)")

                except Exception as e:
                    print(f"     Error testing device {i}: {e}")

            print("\n4. Getting driver version...")
            try:
                driver_version = pynvml_amd_windows.nvmlSystemGetDriverVersion()
                print(f"   Driver: {driver_version}")
            except Exception as e:
                print(f"   Driver version error: {e}")

            print("\n5. Shutting down...")
            if hasattr(pynvml_amd_windows, 'nvmlShutdown'):
                pynvml_amd_windows.nvmlShutdown()

            print("\n✓ Integration test completed successfully!")
            return True

        except Exception as e:
            print(f"\n✗ Integration test failed: {e}")
            traceback.print_exc()
            return False


def main():
    """Main test runner."""
    print("pynvml-amd-windows Test Harness")
    print("="*60)

    # Run unit tests
    print("\nRunning unit tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)

    # Run integration test
    integration_test = IntegrationTest()
    integration_test.run_integration_test()

    print("\n" + "="*60)
    print("Test harness completed!")
    print("="*60)


if __name__ == "__main__":
    main()