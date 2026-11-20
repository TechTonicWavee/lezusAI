from setuptools import setup, find_packages

setup(
    name="drishti-sdk",
    version="1.0.0",
    description="Python client SDK for DRISHTI AI MLOps and AIOps platform",
    author="DRISHTI AI Team",
    packages=find_packages(),
    install_requires=[
        "requests>=2.28.0",
    ],
    python_requires=">=3.8",
)

