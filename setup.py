from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="pynvml-amd-windows",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="pynvml-compatible library for AMD GPUs on Windows",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pynvml-amd-windows",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: System :: Hardware",
        "Topic :: System :: Monitoring",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    keywords="amd gpu nvidia pynvml adlx monitoring hardware",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/pynvml-amd-windows/issues",
        "Source": "https://github.com/yourusername/pynvml-amd-windows",
    },
    platforms=["Windows"],
)
