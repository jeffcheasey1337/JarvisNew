#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS Setup Script
"""

from setuptools import setup, find_packages
from pathlib import Path

# Читаем README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Читаем requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip() 
        for line in requirements_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="jarvis-assistant",
    version="0.1.0",
    author="jeffcheasey1337",
    description="Personal AI Voice Assistant with Learning Capabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jeffcheasey1337/JarvisNew",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "jarvis=jarvis.assistant:main",
        ],
    },
    include_package_data=True,
    package_data={
        "jarvis": ["config/*.json"],
    },
)
