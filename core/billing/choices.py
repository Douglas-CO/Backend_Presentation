IDENTIFICATION_TYPE = (
    ('05', 'CEDULA'),
    ('04', 'RUC'),
    ('06', 'PASAPORTE'),
    ('07', 'VENTA A CONSUMIDOR FINAL*'),
    ('08', 'IDENTIFICACION DELEXTERIOR*'),
)

VOUCHER_TYPE = (
    ('01', 'FACTURA'),
    ('04', 'NOTA DE CRÉDITO'),
    ('08', 'TICKET DE VENTA'),
)

INVOICE_STATUS = (
    ('without_authorizing', 'Sin Autorizar'),
    ('authorized', 'Autorizada'),
    ('authorized_and_sent_by_email', 'Autorizada y enviada por email'),
    ('canceled', 'Anulado'),
    ('sequential_registered_error', 'Error de secuencial registrado'),
)

VOUCHER_STAGE = (
    ('xml_creation', 'Creación del XML'),
    ('xml_signature', 'Firma del XML'),
    ('xml_validation', 'Validación del XML'),
    ('xml_authorized', 'Autorización del XML'),
    ('sent_by_email', 'Enviado por email'),
)

INVOICE_PAYMENT_METHOD = (
    ('01', 'SIN UTILIZACION DEL SISTEMA FINANCIERO'),
    ('15', 'COMPENSACIÓN DE DEUDAS'),
    ('16', 'TARJETA DE DÉBITO'),
    ('17', 'DINERO ELECTRÓNICO'),
    ('18', 'TARJETA PREPAGO'),
    ('20', 'OTROS CON UTILIZACION DEL SISTEMA FINANCIERO'),
    ('21', 'ENDOSO DE TÍTULOS'),
)

CONTRACT_STATUS = (
    ('created', 'Creado'),
    ('active', 'Activo'),
    ('suspended', 'Suspendido'),
    ('finalized', 'Finalizado'),
)

TAX_CODES = (
    (2, 'IVA'),
    (3, 'ICE'),
    (5, 'IRBPNR'),
)

INVOICE_PAYMENT_PAYMENT_METHOD = (
    ('cash', 'Efectivo'),
    ('deposit', 'Deposito'),
    ('transfer', 'Transferencia'),
)

INVOICE_PAYMENT_STATUS = (
    ('grace_period', 'Días de gracia'),
    ('unpaid', 'No pagado'),
    ('paid', 'Pagado'),
)
