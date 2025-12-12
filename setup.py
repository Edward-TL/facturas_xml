"""
Setup configuration for facturas_xml package
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8') if (this_directory / "README.md").exists() else ""

setup(
    name="facturas_xml",
    version="0.3.0",
    author="Edward T.L.",
    author_email="edward_tl@hotmail.com.com",
    description="A Python package for managing and extracting data from Mexican CFDI XML files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",  # Add your repository URL here if you have one
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "python-dotenv>=0.19.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
    },
    keywords="xml cfdi sat mexico invoices facturas",
    project_urls={
        "Bug Reports": "",  # Add issue tracker URL if available
        "Source": "",  # Add source code URL if available
    },
)
