
from setuptools import setup

setup(
    name="drishti-sdk",
    version="1.0.1",
    description="Python client SDK for DRISHTI AI MLOps and AIOps platform",
    author="DRISHTI AI Team",
    packages=["drishti_sdk"],
    package_dir={"drishti_sdk": "."},
    install_requires=[
        "requests>=2.28.0",
    ],
    python_requires=">=3.8",
)
