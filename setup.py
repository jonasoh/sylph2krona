from setuptools import setup

setup(
    name="sylph2krona",
    version="0.1.0",
    description="Convert Sylph profiles to Krona-compatible format using GTDB taxonomy",
    author="Jonas Ohlsson",
    author_email="jonas.ohlsson@slu.se",
    py_modules=["sylph2krona"],
    install_requires=[
        "pandas>=1.3.0",
        "numpy>=1.20.0",
    ],
    entry_points={
        "console_scripts": [
            "sylph2krona=sylph2krona:main",
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
