"""
Comprehensive CFDI 4.0 XML Parser
Extracts all possible data from Mexican SAT CFDI XML files
"""

# This is work in progress, 
# consider that main structure was made with xml_manager_legacy,
# but it was made with Claude Sonnet 4.5
# Now is in revision and upgrading.


from xml.etree import ElementTree
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, List, Any
from facturas_xml.consts import (
    FLOAT_FIELDS,
    INT_FIELDS,
    CONCEPT_FLOAT_FIELDS,
    IMPUESTOS_FLOAT_FIELDS
)


@dataclass
class Xml:
    """
    Comprehensive parser for Mexican CFDI (Comprobante Fiscal Digital por Internet) XML files.
    Supports CFDI 4.0 and extracts all attributes from:
    - Comprobante (root)
    - Emisor (issuer)
    - Receptor (receiver)
    - Conceptos (items/products/services)
    - Impuestos (taxes - both at concept and global level)
    - Complementos (supplements like TimbreFiscalDigital, Pagos, etc.)
    - CfdiRelacionados (related CFDIs)
    """
    file: str | Path
    data: Dict[str, Any] = field(default_factory=dict)
    conceptos: List[Dict[str, Any]] = field(default_factory=list)
    impuestos_conceptos: List[Dict[str, Any]] = field(default_factory=list)
    cfdi_relacionados: List[str] = field(default_factory=list)
    namespaces: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize and parse the XML file"""
        # Default CFDI 4.0 namespaces
        if not self.namespaces:
            self.namespaces = {
                'cfdi': 'http://www.sat.gob.mx/cfd/4',
                'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital',
                'pago20': 'http://www.sat.gob.mx/Pagos20',
                'nomina12': 'http://www.sat.gob.mx/nomina12',
                'cartaporte30': 'http://www.sat.gob.mx/CartaPorte30',
                'leyendasFisc': 'http://www.sat.gob.mx/leyendasFiscales',
                'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
            }
        
        # Parse the XML file
        self.tree = ElementTree.parse(self.file)
        self.root = self.tree.getroot()
        
        # Extract all data
        self._extract_comprobante_attributes()
        self._extract_emisor()
        self._extract_receptor()
        self._extract_conceptos()
        self._extract_impuestos_global()
        self._extract_complemento()
        self._extract_cfdi_relacionados()
        self._extract_addenda()
        
        # Convert field types after all extraction is complete
        self._convert_field_types()
    
    def _clean_key(self, key: str) -> str:
        """Remove namespace prefix from attribute keys"""
        if '}' in key:
            return key.split('}')[1]
        return key
    
    def _should_skip_attribute(self, key: str) -> bool:
        """Check if attribute should be skipped (like Sello, Certificado, etc.)"""
        key_lower = key.lower()
        skip_terms = ['sello', 'certificado', 'http:', 'xsi:', 'schemalocation']
        return any(term in key_lower for term in skip_terms)
    
    def _convert_to_float(self, value: Any) -> float | str:
        """Safely convert a value to float, return original if conversion fails"""
        try:
            return float(value)
        except (ValueError, TypeError):
            return value
    
    def _convert_to_int(self, value: Any) -> int | str:
        """Safely convert a value to int, return original if conversion fails"""
        try:
            return int(value)
        except (ValueError, TypeError):
            return value
    
    def _convert_field_types(self) -> None:
        """
        Convert fields to their appropriate types (float or int) based on 
        float_fields and int_fields attributes. If conversion fails, keeps 
        the original string value.
        """
        # Convert float fields in main data dictionary
        for field_name in FLOAT_FIELDS:
            if field_name in self.data:
                self.data[field_name] = self._convert_to_float(self.data[field_name])
        
        # Convert int fields in main data dictionary
        for field_name in INT_FIELDS:
            if field_name in self.data:
                self.data[field_name] = self._convert_to_int(self.data[field_name])
        
        
        for concepto in self.conceptos:
            for field in CONCEPT_FLOAT_FIELDS:
                if field in concepto:
                    concepto[field] = self._convert_to_float(concepto[field])
            
            # Convert tax amounts in concept-level taxes
            if 'Impuestos' in concepto:
                
                for traslado in concepto['Impuestos'].get('Traslados', []):
                    for field in IMPUESTOS_FLOAT_FIELDS:
                        if field in traslado:
                            traslado[field] = self._convert_to_float(traslado[field])
                
                for retencion in concepto['Impuestos'].get('Retenciones', []):
                    for field in IMPUESTOS_FLOAT_FIELDS:
                        if field in retencion:
                            retencion[field] = self._convert_to_float(retencion[field])
    
    def _extract_comprobante_attributes(self) -> None:
        """
        Extract all attributes from the root Comprobante element.
        Includes: Version, Serie, Folio, Fecha, SubTotal, Moneda, TipoCambio,
        Total, TipoDeComprobante, Exportacion, MetodoPago, FormaPago, 
        LugarExpedicion, Descuento, Condiciones de Pago, etc.
        """
        for key, value in self.root.attrib.items():
            clean_key = self._clean_key(key)
            
            if self._should_skip_attribute(clean_key):
                continue
            
            # Rename Version to avoid conflicts
            if clean_key.lower() == 'version':
                clean_key = 'VersionCFDI'
            
            self.data[clean_key] = value
    
    def _extract_emisor(self) -> None:
        """
        Extract issuer (Emisor) information.
        Includes: Rfc, Nombre, RegimenFiscal
        """
        emisor = self.root.find('cfdi:Emisor', self.namespaces)
        if emisor is not None:
            for key, value in emisor.attrib.items():
                clean_key = self._clean_key(key)
                if 'Emisor' in clean_key:
                    clean_key = clean_key.replace("Emisor", "")

                if not self._should_skip_attribute(clean_key):
                    self.data[f'Emisor{clean_key}'] = value
    
    def _extract_receptor(self) -> None:
        """
        Extract receiver (Receptor) information.
        Includes: Rfc, Nombre, DomicilioFiscalReceptor, RegimenFiscalReceptor, UsoCFDI
        """
        receptor = self.root.find('cfdi:Receptor', self.namespaces)
        if receptor is not None:
            for key, value in receptor.attrib.items():
                clean_key = self._clean_key(key)
                if 'Receptor' in clean_key:
                    clean_key = clean_key.replace("Receptor", "")
                    
                if not self._should_skip_attribute(clean_key):
                    self.data[f'Receptor{clean_key}'] = value
    
    def _extract_conceptos(self) -> None:
        """
        Extract all concepts (Conceptos) - products/services.
        Each concept includes: ClaveProdServ, NoIdentificacion, Cantidad, 
        ClaveUnidad, Unidad, Descripcion, ValorUnitario, Importe, Descuento, ObjetoImp
        Also extracts taxes at concept level (Traslados and Retenciones)
        """
        conceptos_node = self.root.find('cfdi:Conceptos', self.namespaces)
        if conceptos_node is None:
            return
        
        for concepto in conceptos_node.findall('cfdi:Concepto', self.namespaces):
            concepto_data = {}
            
            # Extract concept attributes
            for key, value in concepto.attrib.items():
                clean_key = self._clean_key(key)
                if not self._should_skip_attribute(clean_key):
                    concepto_data[clean_key] = value
            
            # Extract concept-level taxes
            concepto_data['Impuestos'] = self._extract_impuestos_concepto(concepto)
            
            # Extract InformacionAduanera if exists
            info_aduanera = concepto.findall('cfdi:InformacionAduanera', self.namespaces)
            if info_aduanera:
                concepto_data['InformacionAduanera'] = [
                    {self._clean_key(k): v for k, v in info.attrib.items()}
                    for info in info_aduanera
                ]
            
            # Extract CuentaPredial if exists
            cuenta_predial = concepto.find('cfdi:CuentaPredial', self.namespaces)
            if cuenta_predial is not None:
                concepto_data['CuentaPredial'] = {
                    self._clean_key(k): v for k, v in cuenta_predial.attrib.items()
                }
            
            # Extract ACuentaTerceros if exists
            a_cuenta_terceros = concepto.find('cfdi:ACuentaTerceros', self.namespaces)
            if a_cuenta_terceros is not None:
                concepto_data['ACuentaTerceros'] = {
                    self._clean_key(k): v for k, v in a_cuenta_terceros.attrib.items()
                }
            
            self.conceptos.append(concepto_data)
        
        # Create aggregated concept data for backward compatibility
        self._aggregate_conceptos()
    
    def _extract_impuestos_concepto(self, concepto: ElementTree.Element) -> Dict[str, List[Dict]]:
        """Extract taxes at concept level (Traslados and Retenciones)"""
        impuestos = {'Traslados': [], 'Retenciones': []}
        
        impuestos_node = concepto.find('cfdi:Impuestos', self.namespaces)
        if impuestos_node is None:
            return impuestos
        
        # Extract Traslados (transferred taxes like IVA)
        traslados = impuestos_node.find('cfdi:Traslados', self.namespaces)
        if traslados is not None:
            for traslado in traslados.findall('cfdi:Traslado', self.namespaces):
                traslado_data = {
                    self._clean_key(k): v for k, v in traslado.attrib.items()
                }
                impuestos['Traslados'].append(traslado_data)
        
        # Extract Retenciones (withheld taxes)
        retenciones = impuestos_node.find('cfdi:Retenciones', self.namespaces)
        if retenciones is not None:
            for retencion in retenciones.findall('cfdi:Retencion', self.namespaces):
                retencion_data = {
                    self._clean_key(k): v for k, v in retencion.attrib.items()
                }
                impuestos['Retenciones'].append(retencion_data)
        
        return impuestos
    
    def _aggregate_conceptos(self) -> None:
        """Aggregate concept data into single fields for backward compatibility"""
        if not self.conceptos:
            return
        
        # Aggregate common fields
        fields_to_aggregate = [
            'ClaveProdServ', 'NoIdentificacion', 'Cantidad', 'ClaveUnidad',
            'Unidad', 'Descripcion', 'ValorUnitario', 'Importe', 'Descuento', 'ObjetoImp'
        ]
        
        for field in fields_to_aggregate:
            values = [str(c.get(field, '')) for c in self.conceptos if c.get(field)]
            if values:
                self.data[f'{field}Conceptos'] = ' | '.join(values)
    
    def _extract_impuestos_global(self) -> None:
        """
        Extract global taxes (Impuestos at Comprobante level).
        Includes: TotalImpuestosRetenidos, TotalImpuestosTrasladados,
        and detailed Traslados and Retenciones
        """
        impuestos = self.root.find('cfdi:Impuestos', self.namespaces)
        if impuestos is None:
            return
        
        # Extract global tax attributes
        for key, value in impuestos.attrib.items():
            clean_key = self._clean_key(key)
            if not self._should_skip_attribute(clean_key):
                self.data[f'Impuestos{clean_key}'] = value
        
        # Extract Retenciones (withheld taxes)
        retenciones = impuestos.find('cfdi:Retenciones', self.namespaces)
        if retenciones is not None:
            for idx, retencion in enumerate(retenciones.findall('cfdi:Retencion', self.namespaces)):
                for key, value in retencion.attrib.items():
                    clean_key = self._clean_key(key)
                    if not self._should_skip_attribute(clean_key):
                        # If multiple retenciones, add index
                        suffix = f'_{idx}' if idx > 0 else ''
                        self.data[f'{clean_key}Retencion{suffix}'] = value
        
        # Extract Traslados (transferred taxes)
        traslados = impuestos.find('cfdi:Traslados', self.namespaces)
        if traslados is not None:
            for idx, traslado in enumerate(traslados.findall('cfdi:Traslado', self.namespaces)):
                for key, value in traslado.attrib.items():
                    clean_key = self._clean_key(key)
                    if not self._should_skip_attribute(clean_key):
                        # If multiple traslados, add index
                        suffix = f'_{idx}' if idx > 0 else ''
                        self.data[f'{clean_key}Traslado{suffix}'] = value
    
    def _extract_complemento(self) -> None:
        """
        Extract all complements (Complemento).
        Includes: TimbreFiscalDigital, Pagos, Nomina, CartaPorte, etc.
        """
        complemento = self.root.find('cfdi:Complemento', self.namespaces)
        if complemento is None:
            return
        
        # Extract TimbreFiscalDigital (most common)
        self._extract_timbre_fiscal(complemento)
        
        # Extract Pagos 2.0
        self._extract_pagos(complemento)
        
        # Extract Nomina
        self._extract_nomina(complemento)
        
        # Extract CartaPorte
        self._extract_carta_porte(complemento)
        
        # Extract any other complements generically
        self._extract_other_complements(complemento)
    
    def _extract_timbre_fiscal(self, complemento: ElementTree.Element) -> None:
        """Extract TimbreFiscalDigital (PAC stamp)"""
        timbre = complemento.find('tfd:TimbreFiscalDigital', self.namespaces)
        if timbre is not None:
            for key, value in timbre.attrib.items():
                clean_key = self._clean_key(key)
                if self._should_skip_attribute(clean_key):
                    continue
                
                # Rename Version to avoid conflicts
                if clean_key.lower() == 'version':
                    clean_key = 'VersionTimbre'
                
                self.data[f'Timbre{clean_key}'] = value
    
    def _extract_pagos(self, complemento: ElementTree.Element) -> None:
        """Extract Pagos 2.0 complement (payment receipts)"""
        pagos = complemento.find('pago20:Pagos', self.namespaces)
        if pagos is None:
            return
        
        # Extract Pagos attributes
        for key, value in pagos.attrib.items():
            clean_key = self._clean_key(key)
            if clean_key.lower() == 'version':
                clean_key = 'VersionPagos'
            self.data[f'Pagos{clean_key}'] = value
        
        # Extract Totales
        totales = pagos.find('pago20:Totales', self.namespaces)
        if totales is not None:
            for key, value in totales.attrib.items():
                clean_key = self._clean_key(key)
                self.data[f'PagosTotales{clean_key}'] = value
        
        # Extract individual Pago elements
        pagos_list = []
        for pago in pagos.findall('.//pago20:Pago', self.namespaces):
            pago_data = {self._clean_key(k): v for k, v in pago.attrib.items()}
            
            # Extract DoctoRelacionado
            doctos = []
            for docto in pago.findall('pago20:DoctoRelacionado', self.namespaces):
                doctos.append({self._clean_key(k): v for k, v in docto.attrib.items()})
            pago_data['DocumentosRelacionados'] = doctos
            
            pagos_list.append(pago_data)
        
        if pagos_list:
            self.data['PagosDetalle'] = pagos_list
    
    def _extract_nomina(self, complemento: ElementTree.Element) -> None:
        """Extract Nomina complement (payroll)"""
        nomina = complemento.find('nomina12:Nomina', self.namespaces)
        if nomina is not None:
            for key, value in nomina.attrib.items():
                clean_key = self._clean_key(key)
                if clean_key.lower() == 'version':
                    clean_key = 'VersionNomina'
                self.data[f'Nomina{clean_key}'] = value
    
    def _extract_carta_porte(self, complemento: ElementTree.Element) -> None:
        """Extract CartaPorte complement (waybill)"""
        carta_porte = complemento.find('cartaporte30:CartaPorte', self.namespaces)
        if carta_porte is not None:
            for key, value in carta_porte.attrib.items():
                clean_key = self._clean_key(key)
                if clean_key.lower() == 'version':
                    clean_key = 'VersionCartaPorte'
                self.data[f'CartaPorte{clean_key}'] = value
    
    def _extract_other_complements(self, complemento: ElementTree.Element) -> None:
        """Extract any other complements not specifically handled"""
        known_complements = [
            '{http://www.sat.gob.mx/TimbreFiscalDigital}TimbreFiscalDigital',
            '{http://www.sat.gob.mx/Pagos20}Pagos',
            '{http://www.sat.gob.mx/nomina12}Nomina',
            '{http://www.sat.gob.mx/CartaPorte30}CartaPorte'
        ]
        
        for child in complemento:
            if child.tag not in known_complements:
                complement_name = self._clean_key(child.tag)
                for key, value in child.attrib.items():
                    clean_key = self._clean_key(key)
                    if not self._should_skip_attribute(clean_key):
                        self.data[f'{complement_name}{clean_key}'] = value
    
    def _extract_cfdi_relacionados(self) -> None:
        """
        Extract related CFDIs (CfdiRelacionados).
        Includes: TipoRelacion and UUIDs of related documents
        """
        cfdi_relacionados = self.root.find('cfdi:CfdiRelacionados', self.namespaces)
        if cfdi_relacionados is None:
            return
        
        # Extract TipoRelacion
        tipo_relacion = cfdi_relacionados.get('TipoRelacion')
        if tipo_relacion:
            self.data['TipoRelacion'] = tipo_relacion
        
        # Extract all related CFDI UUIDs
        for cfdi_rel in cfdi_relacionados.findall('cfdi:CfdiRelacionado', self.namespaces):
            uuid = cfdi_rel.get('UUID')
            if uuid:
                self.cfdi_relacionados.append(uuid)
        
        # Store as comma-separated string for backward compatibility
        if self.cfdi_relacionados:
            self.data['UUIDCfdiRelacionado'] = ', '.join(self.cfdi_relacionados)
    
    def _extract_addenda(self) -> None:
        """
        Extract Addenda (additional custom data).
        This is optional and varies by issuer
        """
        addenda = self.root.find('cfdi:Addenda', self.namespaces)
        if addenda is not None:
            # Store that addenda exists
            self.data['TieneAddenda'] = 'Sí'
            
            # Try to extract any attributes from addenda children
            for child in addenda:
                addenda_name = self._clean_key(child.tag)
                for key, value in child.attrib.items():
                    clean_key = self._clean_key(key)
                    self.data[f'Addenda{addenda_name}{clean_key}'] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Return all extracted data as a dictionary"""
        return {
            'data': self.data,
            'conceptos': self.conceptos,
            'cfdi_relacionados': self.cfdi_relacionados
        }

    def get_uuid(self) -> Optional[str]:
        """Get the fiscal folio (UUID) from TimbreFiscalDigital"""
        return self.data.get('TimbreUUID')

    def get_total(self) -> Optional[float]:
        """Get the total amount of the CFDI as a float"""
        return self.data.get('Total')

    def get_emisor_rfc(self) -> Optional[str]:
        """Get the RFC of the issuer"""
        return self.data.get('EmisorRfc')

    def get_receptor_rfc(self) -> Optional[str]:
        """Get the RFC of the receiver"""
        return self.data.get('ReceptorRfc')

    def get_fecha(self) -> Optional[str]:
        """Get the issuance date"""
        return self.data.get('Fecha')

    def get_tipo_comprobante(self) -> Optional[str]:
        """Get the type of CFDI (I=Ingreso, E=Egreso, T=Traslado, N=Nomina, P=Pago)"""
        return self.data.get('TipoDeComprobante')


def read_xml_files(files: List[str | Path]) -> Dict[str, List[Any]]:
    """
    Reads a list of XML files and returns a dictionary representing a Series-like structure.
    
    Keys are all fields encountered across all files.
    Values are lists aligned with the input list of files.
    If a field is missing in a specific file, its value will be None.
    
    Args:
        files: List of file paths (strings or Path objects) to parse.
        
    Returns:
        Dict[str, List[Any]]: A dictionary where each key maps to a list of values.
    """
    parsed_lists = {
        'data': [],
        'conceptos': [],
        'cfdi_relacionados': []
    }

    keys = {
        'data': set(),
        'conceptos': set()
    }
    # 1. Parse all files and collect their data dictionaries within the loop
    for file_path in files:
        try:
            # We use the Xml class to ensure we get exactly the same "scrapping" logic
            # and type conversions defined in the project.
            parser = Xml(file_path)
            parsed_lists['data'].append(parser.data)

            # 2. Identify all unique keys encountered across all successfully parsed files
            keys['data'].update(parser.data.keys())

        except Exception as e:
            print(f"Error parsing file data: {file_path}:\n {e.__str__()}")
            # If parsing fails or file is invalid, we append an empty dict
            # to maintain the index alignment with the input 'files' list.
            parsed_lists['data'].append({})

        try:
            for field in ['Folio', 'TimbreUUID', 'Fecha']:
                for concepto in parser.conceptos:
                    if field not in parser.data:
                        print(field, 'not in data')
                    else:
                        concepto[field] = parser.data[field]
            parsed_lists['conceptos'].append(parser.conceptos)

            unique_keys = list({key for d in parser.conceptos for key in d.keys()})
            keys['conceptos'].update(unique_keys)

        except Exception as e:
            print(f"Error parsing file conceptos: {file_path}:\n {e.__str__()}")
            parsed_lists['conceptos'].append([])

    # Sort keys to ensure deterministic order in the output dictionary
    sorted_keys = {
        k: sorted(list(keys[k])) for k in keys.keys()
    }

    # 3. Build the result dictionary
    result = {
        'data': {},
        'conceptos': {},
    }
    for key in sorted_keys['data']:
        result['data'][key] = [data_map.get(key, None) for data_map in parsed_lists['data']]
    
    for key in sorted_keys['conceptos']:
        result['conceptos'][key] = [
            concept.get(key, None) \
                for concepts_list in parsed_lists['conceptos'] \
                    for concept in concepts_list
        ]

    return result
