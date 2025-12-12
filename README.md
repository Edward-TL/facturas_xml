# facturas_xml

A Python package for managing and extracting data from Mexican CFDI (Comprobante Fiscal Digital por Internet) XML files.

## Features

- **File Management**: Utilities for working with files and directories
  - Get files by extension with filtering options
  - List directories
  - Copy directories
  - Flatten nested lists
  - Get all files recursively in a directory tree

- **XML Processing**: Extract data from CFDI XML files
  - Parse Mexican SAT CFDI XML invoices
  - Extract root attributes
  - Extract complements
  - Extract concepts (items)
  - Extract tax information
  - Handle related CFDI documents

## Installation

### Development Installation

To install the package in editable mode (for development):

```bash
pip install -e .
```

This allows you to import the package as `facturas_xml` while still being able to edit the source code.

### Regular Installation

```bash
pip install .
```

### With Development Dependencies

To install with development tools (pytest, black, flake8, mypy):

```bash
pip install -e ".[dev]"
```

## Usage

### Importing the Package

```python
import facturas_xml
from facturas_xml import Xml, get_files, get_all_files_in, xml_read_files
```

### File Management Examples

```python
from facturas_xml import get_files, get_all_files_in, list_directories

# Get all XML files in a directory
xml_files = get_files('/path/to/directory', file_extension='.xml')

# Get all XML files recursively (including subdirectories)
all_xml_files = get_all_files_in('/path/to/root', file_type='.xml')

# List all subdirectories
directories = list_directories('/path/to/directory')
```

### XML Processing Examples

The package includes a comprehensive CFDI 4.0 parser that extracts **all** possible data from Mexican SAT XML files.

```python
from facturas_xml import Xml

# Parse a CFDI XML file
cfdi = Xml(file='/path/to/invoice.xml')

# Access basic information using helper methods
print(cfdi.get_uuid())              # Fiscal folio (UUID)
print(cfdi.get_total())             # Total amount
print(cfdi.get_emisor_rfc())        # Issuer's RFC
print(cfdi.get_receptor_rfc())      # Receiver's RFC
print(cfdi.get_fecha())             # Issuance date
print(cfdi.get_tipo_comprobante())  # Type: I, E, T, N, P

# Access all extracted data
print(cfdi.data)  # Dictionary with ALL extracted fields

# The Xml class automatically extracts:
# ✓ Comprobante attributes (Version, Serie, Folio, Fecha, SubTotal, Total, etc.)
# ✓ Emisor (Rfc, Nombre, RegimenFiscal)
# ✓ Receptor (Rfc, Nombre, DomicilioFiscalReceptor, RegimenFiscalReceptor, UsoCFDI)
# ✓ Conceptos (all products/services with detailed attributes)
# ✓ Impuestos (taxes at both concept and global level)
# ✓ TimbreFiscalDigital (UUID, FechaTimbrado, etc.)
# ✓ Complementos (Pagos, Nomina, CartaPorte, etc.)
# ✓ CfdiRelacionados (related CFDI documents)
# ✓ Addenda (custom additional data)
```

#### Working with Concepts (Products/Services)

```python
# Access all concepts
for concepto in cfdi.conceptos:
    print(concepto['Descripcion'])
    print(concepto['Cantidad'])
    print(concepto['ValorUnitario'])
    print(concepto['Importe'])
    
    # Access taxes for this concept
    for traslado in concepto['Impuestos']['Traslados']:
        print(f"Tax: {traslado['Impuesto']}, Amount: {traslado['Importe']}")
```

#### Working with Complements

```python
# TimbreFiscalDigital (always present in valid CFDIs)
uuid = cfdi.data.get('TimbreUUID')
fecha_timbrado = cfdi.data.get('TimbreFechaTimbrado')

# Pagos (payment receipts)
if 'PagosDetalle' in cfdi.data:
    for pago in cfdi.data['PagosDetalle']:
        print(f"Payment: {pago['Monto']}")
        for docto in pago['DocumentosRelacionados']:
            print(f"Related doc: {docto['IdDocumento']}")

# Nomina (payroll)
if 'NominaTipoNomina' in cfdi.data:
    print(f"Payroll type: {cfdi.data['NominaTipoNomina']}")
```

#### Export to Dictionary/JSON

```python
import json

# Get all data as a structured dictionary
all_data = cfdi.to_dict()

# Export to JSON
with open('cfdi_data.json', 'w', encoding='utf-8') as f:
    json.dump(all_data, f, indent=2, ensure_ascii=False)
```

#### Batch Processing

```python
from facturas_xml import Xml, get_all_files_in

# Get all XML files from a directory (including subdirectories)
xml_files = get_all_files_in('/path/to/invoices', file_type='.xml')

# Process all files
for xml_file in xml_files:
    cfdi = Xml(file=xml_file)
    print(f"{cfdi.get_uuid()}: ${cfdi.get_total()}")
```

Other option is to call the function xml_read_files and it's ready to load into your favorite data frame library:

```python
import pandas as pd
from facturas_xml import xml_read_files

xml_files = get_all_files_in('/path/to/invoices', file_type='.xml')
cfdis_info = xml_read_files(xml_files)

# Load XML General Data into pandas DataFrame
cfdis_data = pd.DataFrame(cfdis_info['data'])

# Load XML Concepts Data into pandas DataFrame
cfdis_concepts = pd.DataFrame(cfdis_info['concepts'])
```


### Legacy XML Parser

The package also includes the original XML parser as `XmlLegacy` for backward compatibility:

```python
from facturas_xml import XmlLegacy

xml_invoice = XmlLegacy(file='/path/to/invoice.xml')
print(xml_invoice.data)
```


## License

MIT License

## Author

Edward T.L. (edward_tl@hotmail.com)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Note

This package is still in development and may have some issues. Please report any issues you find.

This package has nothing to do with the SAT (Servicio de Administración Tributaria) or any other government agency. It is a third-party tool for processing and analyzing XML files.

This package has nothing to do with the project [SAT-CFDI](https://github.com/SAT-CFDI/python-satcfdi/tree/main). This was made just to help me with clients ETL processes, and to guarantee the privacy of they data after and audit.