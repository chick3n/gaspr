from setuptools import find_packages, setup
from pathlib import Path
import sys
    
sys.path.insert(0, ("./gaspr"))
from version import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()


install_requires = [
    'python-dotenv',
    'azure-storage-blob',
    'aiohttp',
    'asyncio',
    'aiofiles',
    'llama_index',
    'openai'
]

setup(
    name='gaspr',  
    version=__version__,
    author="Temp",
    author_email="unknown@unknown.com",
    description="temp",
    install_requires=install_requires,
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
 )