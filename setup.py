import os
import sys
from setuptools import setup, find_packages

# add the src directory to the path so we can import the version
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from sylph2krona import __version__

setup(
    name="sylph2krona",
    version=__version__,
    description="Convert Sylph profiles to Krona-compatible format using GTDB taxonomy",
    author="Jonas Ohlsson",
    author_email="jonas.ohlsson@slu.se",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "pandas>=2.3.0",
    ],
    entry_points={
        "console_scripts": [
            "sylph2krona=sylph2krona.sylph2krona:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
)
