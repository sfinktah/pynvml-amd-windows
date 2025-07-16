# pynvml-amd-windows

## Purpose

**pynvml-amd-windows** is a drop-in replacement for NVIDIA's `pynvml` Python library, designed to allow existing pynvml-based applications to monitor and manage AMD GPUs on Windows systems. It provides a compatible API that redirects NVML calls to the AMD ADLX backend, enabling tools that were written for NVIDIA GPUs to work seamlessly with AMD hardware.

It was written for the specific purpose of enabling [Crystools](https://github.com/crystian/ComfyUI-Crystools) GPU performance monitoring for AMD platforms under Windows.

This package is especially useful if you have tools or scripts that expect `pynvml` to be present, and you want them to function without modification on systems with supported AMD GPUs.

## Features

- Implements the `pynvml` interface using AMD's ADLX library for Windows.
- Compatible with most scripts and programs expecting `import pynvml`.
- No need to modify existing code: the package transparently handles imports using a `.pth` file.

## Installation

### Using pip
```
pip install pynvml-amd-windows
```

### From source

Clone or download this repository, then run:
```
pip install .
```
from within the project directory.

## Usage

After installation, any Python program that imports `pynvml` (or uses a package depending on it) will transparently use the AMD implementation on Windows—no code changes required.

Example:
```
python
import pynvml

pynvml.nvmlInit()
count = pynvml.nvmlDeviceGetCount()
print("Number of AMD GPUs detected:", count)
```
## Limitations

- Only supports AMD GPUs on Windows using the ADLX backend.
- Some advanced `pynvml` features may not be supported or may have slightly different behavior due to backend differences.

## License

This project is distributed under the MIT License.

## Authors

- Christopher Anderson (<sfinktah@github.spamtrak.org>)
```

