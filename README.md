# pynvml-amd-windows

A pynvml-compatible library for AMD GPUs on Windows using ADLX (AMD Device Library eXtra).

## Overview

This library provides a drop-in replacement for pynvml when working with AMD GPUs on Windows. It uses the ADLX library to provide the same interface as pynvml, allowing existing applications to work with AMD hardware without modification.

## Installation

```bash
pip install pynvml-amd-windows
```

## Requirements

- Windows operating system
- AMD GPU with ADLX support
- Python 3.7+
- ADLXPybind package

## Usage

Simply replace your pynvml import with this library:

```python
# Instead of: import pynvml
import pynvml_amd_windows as pynvml

# Initialize
pynvml.nvmlInit()

# Get device count
device_count = pynvml.nvmlDeviceGetCount()
print(f"Number of GPUs: {device_count}")

# Get device handle
handle = pynvml.nvmlDeviceGetHandleByIndex(0)

# Get device name
name = pynvml.nvmlDeviceGetName(handle)
print(f"GPU Name: {name}")

# Get temperature
temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
print(f"Temperature: {temp}°C")

# Get utilization
util = pynvml.nvmlDeviceGetUtilizationRates(handle)
print(f"GPU Utilization: {util.gpu}%")

# Get memory info
mem = pynvml.nvmlDeviceGetMemoryInfo(handle)
print(f"Memory: {mem.used}/{mem.total} bytes")

# Shutdown
pynvml.nvmlShutdown()
```

## Supported Functions

- `nvmlInit()` - Initialize ADLX library
- `nvmlDeviceGetCount()` - Get number of GPU devices
- `nvmlDeviceGetHandleByIndex(index)` - Get device handle by index
- `nvmlDeviceGetName(handle)` - Get device name
- `nvmlSystemGetDriverVersion()` - Get driver version
- `nvmlDeviceGetUtilizationRates(handle)` - Get GPU utilization
- `nvmlDeviceGetMemoryInfo(handle)` - Get memory information
- `nvmlDeviceGetTemperature(handle, sensor)` - Get temperature
- `nvmlShutdown()` - Shutdown library

## Limitations

- Windows only
- AMD GPUs only
- Some pynvml functions may not be available
- Memory utilization in `nvmlDeviceGetUtilizationRates()` always returns 0

## License

MIT License

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
