"""
"""
import itertools

FLOAT_FIELDS = (
    "Subtotal",
    "Total",
    "VersionCFDI",
    "DI",
    "VersionComplemento",
    "CantidadConceptos",
    "ValorUnitarioConceptos",
    "ImporteConceptos",
    "ImpuestosTotalImpuestosTrasladados",
    "BaseTraslado",
    "ImporteTraslado",
    "ImpuestoTraslado",
    "TasaOCuotaTraslado",
    "TimbreVersionTimbre",
    "Descuento",
    "DescuentoConceptos",
    "CartaPorteVersion",
    "CartaPorteTotalDistRec",

)

INT_FIELDS = (
    "Folio",
    "LugarExpedicion",
    "EmisorRegimenFiscal",
    "ReceptorDomicilioFiscalReceptor",
    "ReceptorRegimenFiscalReceptor",

)

# numeric_concepto_fields = {
#             'Cantidad': 'float',
#             'ValorUnitario': 'float',
#             'Importe': 'float',
#             'Descuento': 'float'
#         }
        

CONCEPT_FLOAT_FIELDS = (
    "Cantidad",
    "ValorUnitario",
    "Importe",
    "Descuento"
)

IMPUESTOS_FLOAT_FIELDS = (
    "Base",
    "Importe",
    "TasaOCuota"
)

