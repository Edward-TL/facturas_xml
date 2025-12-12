"""
Example usage of the facturas_xml package with the new comprehensive Xml class
"""
from facturas_xml import Xml, get_all_files_in
from pathlib import Path
import json


def example_single_xml():
    """Example: Parse a single CFDI XML file"""
    print("=" * 60)
    print("Example 1: Parsing a single CFDI XML file")
    print("=" * 60)
    
    # Replace with your actual XML file path
    xml_file = "path/to/your/factura.xml"
    
    # Parse the XML
    cfdi = Xml(file=xml_file)
    
    # Access basic information
    print(f"\nUUID: {cfdi.get_uuid()}")
    print(f"Emisor RFC: {cfdi.get_emisor_rfc()}")
    print(f"Receptor RFC: {cfdi.get_receptor_rfc()}")
    print(f"Fecha: {cfdi.get_fecha()}")
    print(f"Total: ${cfdi.get_total()}")
    print(f"Tipo: {cfdi.get_tipo_comprobante()}")
    
    # Access all extracted data
    print(f"\nTotal fields extracted: {len(cfdi.data)}")
    print(f"Number of concepts: {len(cfdi.conceptos)}")
    print(f"Related CFDIs: {len(cfdi.cfdi_relacionados)}")
    
    # Print some key fields
    print("\n--- Key Fields ---")
    for key in ['Serie', 'Folio', 'Moneda', 'MetodoPago', 'FormaPago', 'LugarExpedicion']:
        if key in cfdi.data:
            print(f"{key}: {cfdi.data[key]}")
    
    # Print concepts
    print("\n--- Conceptos ---")
    for i, concepto in enumerate(cfdi.conceptos, 1):
        print(f"\nConcepto {i}:")
        print(f"  Descripción: {concepto.get('Descripcion', 'N/A')}")
        print(f"  Cantidad: {concepto.get('Cantidad', 'N/A')}")
        print(f"  Valor Unitario: ${concepto.get('ValorUnitario', 'N/A')}")
        print(f"  Importe: ${concepto.get('Importe', 'N/A')}")
        
        # Print taxes for this concept
        if concepto.get('Impuestos'):
            traslados = concepto['Impuestos'].get('Traslados', [])
            if traslados:
                print(f"  Impuestos Trasladados: {len(traslados)}")
                for traslado in traslados:
                    print(f"    - {traslado.get('Impuesto', 'N/A')}: ${traslado.get('Importe', 'N/A')}")


def example_batch_processing():
    """Example: Process multiple XML files from a directory"""
    print("\n" + "=" * 60)
    print("Example 2: Batch processing multiple XML files")
    print("=" * 60)
    
    # Replace with your directory path
    xml_directory = "path/to/your/xml/files"
    
    # Get all XML files
    xml_files = get_all_files_in(xml_directory, file_type='.xml')
    
    print(f"\nFound {len(xml_files)} XML files")
    
    # Process each file
    results = []
    for xml_file in xml_files[:5]:  # Process first 5 as example
        try:
            cfdi = Xml(file=xml_file)
            results.append({
                'file': Path(xml_file).name,
                'uuid': cfdi.get_uuid(),
                'emisor': cfdi.get_emisor_rfc(),
                'receptor': cfdi.get_receptor_rfc(),
                'total': cfdi.get_total(),
                'fecha': cfdi.get_fecha(),
                'tipo': cfdi.get_tipo_comprobante()
            })
        except Exception as e:
            print(f"Error processing {xml_file}: {e}")
    
    # Display results
    print("\n--- Processing Results ---")
    for result in results:
        print(f"\nFile: {result['file']}")
        print(f"  UUID: {result['uuid']}")
        print(f"  Emisor: {result['emisor']}")
        print(f"  Total: ${result['total']}")


def example_export_to_json():
    """Example: Export CFDI data to JSON"""
    print("\n" + "=" * 60)
    print("Example 3: Export CFDI data to JSON")
    print("=" * 60)
    
    xml_file = "path/to/your/factura.xml"
    
    # Parse the XML
    cfdi = Xml(file=xml_file)
    
    # Get all data as dictionary
    data = cfdi.to_dict()
    
    # Save to JSON
    output_file = "cfdi_data.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\nData exported to: {output_file}")
    print(f"Total fields: {len(data['data'])}")
    print(f"Concepts: {len(data['conceptos'])}")


def example_filter_by_criteria():
    """Example: Filter CFDIs by specific criteria"""
    print("\n" + "=" * 60)
    print("Example 4: Filter CFDIs by criteria")
    print("=" * 60)
    
    xml_directory = "path/to/your/xml/files"
    xml_files = get_all_files_in(xml_directory, file_type='.xml')
    
    # Filter: Find all "Ingreso" type CFDIs with total > 10000
    filtered = []
    for xml_file in xml_files:
        try:
            cfdi = Xml(file=xml_file)
            
            if (cfdi.get_tipo_comprobante() == 'I' and 
                float(cfdi.get_total() or 0) > 10000):
                filtered.append({
                    'file': Path(xml_file).name,
                    'uuid': cfdi.get_uuid(),
                    'total': cfdi.get_total(),
                    'emisor': cfdi.data.get('EmisorNombre', 'N/A')
                })
        except Exception as e:
            continue
    
    print(f"\nFound {len(filtered)} CFDIs matching criteria")
    for item in filtered[:10]:  # Show first 10
        print(f"\n{item['file']}")
        print(f"  Total: ${item['total']}")
        print(f"  Emisor: {item['emisor']}")


if __name__ == "__main__":
    print("CFDI XML Parser - Usage Examples")
    print("=" * 60)
    print("\nNote: Update the file paths in the examples before running")
    print("=" * 60)
    
    # Uncomment the examples you want to run:
    # example_single_xml()
    # example_batch_processing()
    # example_export_to_json()
    # example_filter_by_criteria()
    
    print("\n\nTo run examples, uncomment the function calls at the bottom of this file")
