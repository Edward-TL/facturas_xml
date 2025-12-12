"""
Docstring para xml_manager
"""
from xml.etree import ElementTree
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


from .file_manager import get_all_files_in

def check_xml_core(k: str) -> bool:
        if not any(
            [
                'sello' in k.lower(),
                'certificado' == k.lower(),
                "http:" in k.lower()
                ]
                ):
            return True
        
        return False

@dataclass
class Xml:
    """
    Abstract of an XML file
    """
    file: str | Path
    data: dict = field(default_factory={})
    key_sort: list = field(default_factory=[])
    namespaces: dict = field(
        default_factory={'cfdi': 'http://www.sat.gob.mx/cfd/4'}
        )
    prefix: Optional[str] = None
    def __post_init__(self):
        """
        Need post_init configuration or 'hot start'
        """
        if self.prefix is None:
            self.prefix = "{" + self.namespaces['cfdi'] + "}"

        self.root = ElementTree.parse(self.file).getroot()
        self.extract_root_attributes()
        self.extract_root_complements()
        self.extract_xml_data()

    def extract_root_attributes(self) -> None:
        """
        Docstring para extract_root_attributes
        
        :param self: Descripción
        :param root: Descripción
        :type root: ElementTree
        """

        for k,v in self.root.attrib.items():
            if check_xml_core(k):
                # print("* ",k,":", v)
                if k.lower() == 'version':
                    k = 'VersionCFDI'
                self.data[k] = v
                self.key_sort.append(k)

    def extract_root_complements(self):
        """
        Docstring para extract_root_complements
        
        :param self: Descripción
        """
        complemento = self.root.findall(".//cfdi:Complemento", self.namespaces)[0]
        for child in complemento:
            for k,v in child.attrib.items():
                if check_xml_core(k):
                    # print("* ",k,":", v)

                    if k in self.data:
                        print(f"WARNING!! OVER-WRITING {k} in {self.file}")
                    if k.lower() == 'version':
                        k = 'VersionComplemento'
                    self.data[k] = v
                    self.key_sort.append(k)

    def concecpt_extraction(self, child: ElementTree, child_tag: str):
        """
        Docstring para concecpt_extraction
        
        :param self: Descripción
        """
        # print(f"`{len(child)} {child_tag}`")
        concepts_atts = {}
        concepts_taxes = {}
        for n, concept in enumerate(child):
            
            # print(f"{n+1}.- {concept.attrib['Descripcion']}")
            # Se genera el concepts_atts, para despues concatenarlos en una sola columna

            for k,v in concept.attrib.items():
                # print("* ",k,":", v)
                if k in concepts_atts:
                    concepts_atts[k].append(v)
                else:
                    concepts_atts[k] = [v]

            impuesto_trasladado = concept.findall(".//cfdi:Traslado", self.namespaces)
            if len(impuesto_trasladado) > 0:
                impuesto_trasladado = impuesto_trasladado[0]
                # print("Impuestos del Concepto")
                for k, v in impuesto_trasladado.attrib.items():
                    if k in concepts_taxes:
                        concepts_taxes[k].append(v)
                    else:
                        concepts_taxes[k] = [v]
                    # print("* ",k,":", v)

            # print()
        
        for k, v in concepts_atts.items():
            k = f"{k}Conceptos"
            if k in self.data:
                print(f"WARNING!! OVER-WRITING {k} in {self.file}")
            self.data[k] = " * ".join(v)
            self.key_sort.append(k)

        for k, v in concepts_taxes.items():
            k = f"{k}Conceptos"
            if k in self.data:
                print(f"WARNING!! OVER-WRITING {k} in {self.file}")
            self.data[k] = " * ".join(v)
            self.key_sort.append(k)
    
    def taxes_extraction(self, child: ElementTree, child_tag: str):
        """
        Docstring para taxes_extraction
        
        :param self: Descripción
        :param child: Descripción
        :type child: ElementTree
        """
        for concept in child:
            impuesto_trasladado = concept.findall(".//cfdi:Traslado", self.namespaces)
            if len(impuesto_trasladado) > 0:
                impuesto_trasladado = impuesto_trasladado[0]
                # print("Impuestos Totales")
                for k, v in impuesto_trasladado.attrib.items():
                    # print("* ",k,":", v)

                    if k in self.data:
                        print(f"WARNING!! OVER-WRITING {k} in {self.file}")
                    self.data[k] = v
                    self.key_sort.append(k)

    def others_extraction(self, child: ElementTree, child_tag: str):
        for k,v in child.attrib.items():
            if not child_tag in k:
                k = f"{k}{child_tag}"
            # print("* ",k,":", v)

            if k in self.data:
                print(f"WARNING!! OVER-WRITING {k} in {self.file}")
            self.data[k] = v
            self.key_sort.append(k)


    def related_extraction(self, child: ElementTree):
        """
        Docstring para complement_extraction
        
        :param self: Descripción
        :param child: Descripción
        :type child: ElementTree
        """
        cfdi_relacionado = child.findall(".//cfdi:CfdiRelacionado", self.namespaces)
        if len(cfdi_relacionado) > 0:
            cfdi_relacionado = cfdi_relacionado[0]
            for k, v in cfdi_relacionado.attrib.items():
                k = f"{k}CfdiRelacionado"
                # print("* ",k,":", v)

                if k in self.data:
                    print(f"WARNING!! OVER-WRITING {k} in {self.file}")
                self.data[k] = v
                self.key_sort.append(k)

        
    def extract_xml_data(self):
        """
        Docstring para extract_self.data
        
        :param root: Descripción
        :param self.file: Descripción
        :type self.file: str
        :param self.namespaces: Descripción
        :type self.namespaces: dict
        :param prefix: Descripción
        :type prefix: str
        """

        for child in self.root:
            child_tag = child.tag.removeprefix(self.prefix)
            if child_tag == 'Conceptos':
                self.concecpt_extraction(child, child_tag)
            elif child_tag == 'Impuestos':
                self.taxes_extraction(child, child_tag)

            elif child_tag == 'Complemento':
                pass

            else:
                # print(f"`{child_tag}`")
                if child_tag == "CfdiRelacionados":
                    self.related_extraction(child)
                else:
                    self.others_extraction(child, child_tag)