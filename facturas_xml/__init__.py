"""
facturas_xml - A Python package for managing and extracting data from Mexican CFDI XML files.

This package provides utilities for:
- File management operations
- XML parsing and data extraction from CFDI (Comprobante Fiscal Digital por Internet) files
"""

from .file_manager import (
    parent_dir,
    get_config,
    get_files,
    list_directories,
    copy_directory,
    flat_list,
    get_all_files_in
)

from .xml_manager_legacy import (
    Xml as XmlLegacy,
    check_xml_core
)

from .xml_manager import (
    Xml,
    read_xml_files
)

__version__ = "0.3.0"
__author__ = "Edward T.L."

__all__ = [
    # File manager functions
    "parent_dir",
    "get_config",
    "get_files",
    "list_directories",
    "copy_directory",
    "flat_list",
    "get_all_files_in",
    # XML manager classes and functions (new comprehensive version)
    "Xml",
    "read_xml_files",
    # Legacy XML manager
    "XmlLegacy",
    "check_xml_core",
]
