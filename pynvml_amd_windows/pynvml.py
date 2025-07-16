"""
ADLX to pynvml compatibility module.

This module provides a pynvml-compatible interface using ADLXPybind for AMD GPUs.
It emulates the pynvml functions needed for GPU monitoring applications.
"""

import ADLXPybind as ADLX
from typing import Optional, Dict, Any


class NvmlException(Exception):
    """Exception raised for NVML/ADLX errors."""
    pass


class UtilizationRates:
    """Emulates pynvml.nvmlUtilization_t structure."""
    
    def __init__(self, gpu_utilization: float = 0.0, memory_utilization: float = 0.0):
        self.gpu = int(gpu_utilization)
        self.memory = int(memory_utilization)


class MemoryInfo:
    """Emulates pynvml.nvmlMemory_t structure."""
    
    def __init__(self, total: int = 0, used: int = 0, free: int = 0):
        self.total = total
        self.used = used
        self.free = free


class DeviceHandle:
    """Represents a GPU device handle."""
    
    def __init__(self, gpu_obj, index: int):
        self.index = index
        self.name = None
        self._gpu_weak_ref = None  # Don't store strong reference
        self._cache_name(gpu_obj)
    
    def _cache_name(self, gpu_obj):
        """Cache the GPU name for performance."""
        try:
            if gpu_obj:
                self.name = gpu_obj.Name()
        except Exception:
            self.name = f"AMD GPU {self.index}"
    
    def __del__(self):
        """Cleanup - but avoid accessing potentially invalid ADLX objects."""
        # Don't try to delete GPU objects here - let ADLX handle its own cleanup
        pass


class ADLXToPynvml:
    """
    Main class that provides pynvml-compatible interface using ADLXPybind.
    """

    # Constants to match pynvml
    NVML_TEMPERATURE_GPU = 0

    def __init__(self):
        self._initialized = False
        self._adlx_helper = None
        self._system = None
        self._gpu_holder = None
        self._gpu_list = None
        self._perf_monitoring = None
        self._device_handles = {}
        self._gpu_vram_ranges = {}  # Cache for GPU VRAM ranges {gpu_index: max_vram_mb}
        self._vram_cache_populated = False  # Flag to track if cache has been populated

    def _cache_gpu_vram_ranges(self):
        """Cache VRAM ranges for all GPUs during initialization."""
        # Only cache if we haven't already cached for this initialization
        if self._vram_cache_populated:
            return

        if not self._perf_monitoring or not self._gpu_list:
            return

        try:
            # Get count directly instead of calling nvmlDeviceGetCount to avoid circular dependency
            gpu_count = 0
            if hasattr(self._gpu_list, 'Size'):
                gpu_count = self._gpu_list.Size()
            elif hasattr(self._gpu_list, 'GetCount'):
                gpu_count = self._gpu_list.GetCount()
            else:
                # Fallback: count by iterating
                try:
                    while True:
                        gpu = self._gpu_list.At(gpu_count)
                        if gpu is None:
                            break
                        del gpu
                        gpu_count += 1
                except:
                    pass

            # print(f"DEBUG: Caching VRAM ranges for {gpu_count} GPUs")

            for i in range(gpu_count):
                try:
                    gpu = self._gpu_list.At(i)
                    if gpu:
                        support = self._perf_monitoring.GetSupportedGPUMetrics(gpu)
                        if support:
                            try:
                                _, max_vram_mb = support.GetGPUVRAMRange()
                                self._gpu_vram_ranges[i] = max_vram_mb
                                # print(f"DEBUG: Cached VRAM range for GPU {i}: {max_vram_mb} MB")
                            except Exception as e:
                                # print(f"DEBUG: Failed to get VRAM range for GPU {i}: {e}")
                                self._gpu_vram_ranges[i] = 0

                            if hasattr(support, 'Release'):
                                support.Release()
                            del support
                        else:
                            # print(f"DEBUG: Failed to get metrics support for GPU {i}")
                            self._gpu_vram_ranges[i] = 0

                        del gpu
                    else:
                        # print(f"DEBUG: Failed to get GPU object for index {i}")
                        self._gpu_vram_ranges[i] = 0
                except Exception as e:
                    # print(f"DEBUG: Exception caching VRAM range for GPU {i}: {e}")
                    self._gpu_vram_ranges[i] = 0

            # Mark cache as populated
            self._vram_cache_populated = True

        except Exception as e:
            print(f"DEBUG: Exception in _cache_gpu_vram_ranges: {e}")

    def nvmlInit(self) -> None:
        """Initialize ADLX library (emulates nvmlInit)."""
        if self._initialized:
            return

        try:
            self._adlx_helper = ADLX.ADLXHelper()
            res = self._adlx_helper.Initialize()

            if res != ADLX.ADLX_RESULT.ADLX_OK:
                raise NvmlException(f"ADLX initialization failed: {res}")

            self._system = self._adlx_helper.GetSystemServices()
            if not self._system:
                raise NvmlException("Failed to get ADLX system services")

            self._gpu_holder = ADLX.ADLXGPUHolder(self._system)
            if not self._gpu_holder.isValid():
                raise NvmlException("Failed to create GPU holder")

            self._gpu_list = self._gpu_holder.getGPUList()
            if not self._gpu_list:
                raise NvmlException("Failed to get GPU list")

            self._perf_monitoring = self._system.GetPerformanceMonitoringServices()

            # Cache GPU VRAM ranges for all GPUs
            self._cache_gpu_vram_ranges()

            self._initialized = True

        except Exception as e:
            self._cleanup()
            raise NvmlException(f"ADLX initialization error: {str(e)}")

    # ... rest of the methods properly indented inside the class
    def nvmlDeviceGetCount(self) -> int:
        """
        Get the number of AMD GPU devices available.
        
        Returns:
            int: Number of GPU devices
            
        Raises:
            NvmlException: If not initialized or error occurs
        """
        if not self._initialized:
            raise NvmlException("ADLX not initialized")
    
        try:
            if not self._gpu_list:
                return 0
            
            # Try different methods to get count based on ADLX API
            if hasattr(self._gpu_list, 'Size'):
                return self._gpu_list.Size()
            elif hasattr(self._gpu_list, 'GetCount'):
                return self._gpu_list.GetCount()
            else:
                # Fallback: count by iterating through the list
                count = 0
                try:
                    while True:
                        gpu = self._gpu_list.At(count)
                        if gpu is None:
                            break
                        count += 1
                    
                except:
                    # If At() throws an exception, we've reached the end
                    pass
                return count
            
        except Exception as e:
            raise NvmlException(f"Failed to get device count: {str(e)}")
    
    def nvmlDeviceGetHandleByIndex(self, index: int) -> DeviceHandle:
        """Get device handle by index using correct ADLX API."""
        if not self._initialized:
            raise NvmlException("NVML not initialized")

        try:
            # Get GPU count for bounds checking
            gpu_count = self.nvmlDeviceGetCount()
            if index >= gpu_count:
                raise NvmlException(f"Device index {index} out of range (max: {gpu_count-1})")

            # Get GPU object temporarily
            gpu = self._gpu_list.At(index)
            if gpu is None:
                raise NvmlException(f"Failed to get GPU at index {index}")

            # Create device handle without storing GPU object reference
            handle = DeviceHandle(gpu, index)
        
            # Don't store the GPU object in the handle - let it go out of scope
            return handle

        except Exception as e:
            raise NvmlException(f"Failed to get device handle: {str(e)}")
    
    def nvmlDeviceGetName(self, device_handle: DeviceHandle) -> str:
        """
        Get device name.
        
        Args:
            device_handle (DeviceHandle): Device handle
            
        Returns:
            str: GPU device name
            
        Raises:
            NvmlException: If error occurs
        """
        if not self._initialized:
            raise NvmlException("ADLX not initialized")
        
        try:
            if device_handle.name:
                return device_handle.name
            return f"AMD GPU {device_handle.index}"
        except Exception as e:
            raise NvmlException(f"Failed to get device name: {str(e)}")
    
    def nvmlSystemGetDriverVersion(self) -> str:
        """
        Get AMD driver version.
        
        Returns:
            str: Driver version string
            
        Raises:
            NvmlException: If error occurs
        """
        if not self._initialized:
            raise NvmlException("ADLX not initialized")
        
        try:
            # ADLX doesn't directly provide driver version, return placeholder
            return "AMD Driver: Unknown"
        except Exception as e:
            raise NvmlException(f"Failed to get driver version: {str(e)}")
    
    def _get_gpu_by_index(self, index: int):
        """Helper method to get a fresh GPU object by index."""
        if not self._initialized:
            raise NvmlException("ADLX not initialized")
        
        gpu = self._gpu_list.At(index)
        if gpu is None:
            raise NvmlException(f"Failed to get GPU at index {index}")
        return gpu

    def nvmlDeviceGetUtilizationRates(self, device_handle: DeviceHandle) -> UtilizationRates:
        """Get GPU utilization rates."""
        if not self._initialized:
            raise NvmlException("ADLX not initialized")
        
        try:
            gpu_utilization = 0.0
            memory_utilization = 0.0
        
            if self._perf_monitoring:
                try:
                    # Get fresh GPU object for this operation
                    gpu = self._get_gpu_by_index(device_handle.index)
                
                    metrics = self._perf_monitoring.GetCurrentGPUMetrics(gpu)
                    if metrics:
                        gpu_utilization = metrics.GPUUsage()
                    
                        # Calculate memory utilization percentage using cached VRAM range
                        try:
                            used_vram_mb = metrics.GPUVRAM()  # VRAM usage in MB
                            max_vram_mb = self._gpu_vram_ranges.get(device_handle.index, 0)
                        
                            if max_vram_mb > 0:
                                memory_utilization = (used_vram_mb / max_vram_mb) * 100.0
                            else:
                                print("DEBUG: Max VRAM is 0, cannot calculate memory utilization")
                            
                        except Exception as e:
                            # print(f"DEBUG: Exception calculating memory utilization: {e}")
                            pass  # If VRAM calculation fails, keep memory_utilization as 0
                    
                        # Clean up metrics
                        if hasattr(metrics, 'Release'):
                            metrics.Release()
                        del metrics
                
                    # Clean up GPU object
                    del gpu
                
                except Exception as e:
                    print(f"DEBUG: Exception in nvmlDeviceGetUtilizationRates: {e}")
                    pass  # Ignore errors, return default values
        
            return UtilizationRates(gpu_utilization, memory_utilization)
        
        except Exception as e:
            raise NvmlException(f"Failed to get utilization rates: {str(e)}")

    def nvmlDeviceGetMemoryInfo(self, device_handle: DeviceHandle) -> MemoryInfo:
        """Get GPU memory information."""
        if not self._initialized:
            raise NvmlException("ADLX not initialized")
        
        try:
            total_memory = 0
            used_memory = 0
            
            if self._perf_monitoring:
                try:
                    # Get fresh GPU object for this operation
                    gpu = self._get_gpu_by_index(device_handle.index)
                    
                    metrics = self._perf_monitoring.GetCurrentGPUMetrics(gpu)
                    if metrics:
                        used_memory = metrics.GPUVRAM() * 1024 * 1024  # Convert MB to bytes
                        
                        # Use cached VRAM range instead of querying every time
                        max_vram_mb = self._gpu_vram_ranges.get(device_handle.index, 0)
                        total_memory = max_vram_mb * 1024 * 1024  # Convert MB to bytes
                        
                        # Clean up metrics
                        if hasattr(metrics, 'Release'):
                            metrics.Release()
                        del metrics
                    
                    # Clean up GPU object
                    del gpu
                    
                except Exception:
                    pass  # Ignore errors, return default values
            
            free_memory = max(0, total_memory - used_memory)
            return MemoryInfo(total_memory, used_memory, free_memory)
            
        except Exception as e:
            raise NvmlException(f"Failed to get memory info: {str(e)}")

    def nvmlDeviceGetTemperature(self, device_handle: DeviceHandle, temperature_type: int) -> int:
        """Get GPU temperature."""
        if not self._initialized:
            raise NvmlException("ADLX not initialized")
        
        try:
            temperature = 0
        
            if self._perf_monitoring:
                try:
                    # Get fresh GPU object for this operation
                    gpu = self._get_gpu_by_index(device_handle.index)
                
                    metrics = self._perf_monitoring.GetCurrentGPUMetrics(gpu)
                    if metrics:
                        temperature = int(metrics.GPUTemperature())
                    
                        # Clean up metrics
                        if hasattr(metrics, 'Release'):
                            metrics.Release()
                        del metrics
                
                    # Clean up GPU object
                    del gpu
                
                except Exception:
                    pass  # Ignore errors, return default value
        
            return temperature
        
        except Exception as e:
            raise NvmlException(f"Failed to get temperature: {str(e)}")
    
    def nvmlShutdown(self) -> None:
        """
        Shutdown ADLX library.
        
        Raises:
            NvmlException: If error occurs during shutdown
        """
        try:
            self._cleanup()
        except Exception as e:
            raise NvmlException(f"Failed to shutdown ADLX: {str(e)}")
    
    def _cleanup(self):
        """Clean up ADLX resources."""
        try:
            # Clear cached ranges and reset flag
            self._gpu_vram_ranges.clear()
            self._vram_cache_populated = False

            # Clean up ADLX objects
            if self._gpu_list:
                del self._gpu_list
                self._gpu_list = None

            if self._gpu_holder:
                del self._gpu_holder
                self._gpu_holder = None

            if self._perf_monitoring:
                del self._perf_monitoring
                self._perf_monitoring = None

            if self._system:
                del self._system
                self._system = None

            if self._adlx_helper:
                try:
                    self._adlx_helper.Terminate()
                except Exception:
                    pass
                del self._adlx_helper
                self._adlx_helper = None

            self._initialized = False

        except Exception:
            pass  # Ignore cleanup errors


# Create global instance to match pynvml usage pattern
_adlx_instance = ADLXToPynvml()

# Expose functions at module level to match pynvml API
def nvmlInit():
    """Initialize ADLX library."""
    return _adlx_instance.nvmlInit()

def nvmlDeviceGetCount():
    """Get number of GPU devices."""
    return _adlx_instance.nvmlDeviceGetCount()

def nvmlDeviceGetHandleByIndex(index: int):
    """Get device handle by index."""
    return _adlx_instance.nvmlDeviceGetHandleByIndex(index)

def nvmlDeviceGetName(device_handle):
    """Get device name."""
    return _adlx_instance.nvmlDeviceGetName(device_handle)

def nvmlSystemGetDriverVersion():
    """Get driver version."""
    return _adlx_instance.nvmlSystemGetDriverVersion()

def nvmlDeviceGetUtilizationRates(device_handle):
    """Get utilization rates."""
    return _adlx_instance.nvmlDeviceGetUtilizationRates(device_handle)

def nvmlDeviceGetMemoryInfo(device_handle):
    """Get memory information."""
    return _adlx_instance.nvmlDeviceGetMemoryInfo(device_handle)

def nvmlDeviceGetTemperature(device_handle, temperature_type):
    """Get temperature."""
    return _adlx_instance.nvmlDeviceGetTemperature(device_handle, temperature_type)

def nvmlShutdown():
    """Shutdown ADLX library."""
    return _adlx_instance.nvmlShutdown()

# Constants
NVML_TEMPERATURE_GPU = ADLXToPynvml.NVML_TEMPERATURE_GPU