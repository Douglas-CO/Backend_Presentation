IDENTIFICATION_TYPE = (
    ('CEDULA', 'Cedula'),
    ('RUC', 'RUC'),
    ('PASAPORTE', 'Pasaporte'),
)
# ### ROLES - users - filter data
USER_ROLES = (
    ('GERENCIA', 'Gerencia'),  # all business
    ('ADMINISTRADOR', 'Administrador'),  # all area
    ('COORDINADOR', 'Coordinador'),  # all department
    ('SUPERVISOR', 'Supervisor'),  # all sales channel
    ('AGENTE', 'Agente'),  # all created by himself (vendedor)


    ('TECNICO', 'Tecnico'),  # filter all created by himself
    ('OPERACIONES', 'Operaciones'),
    ('PLANTA EXTERNA', 'Planta Externa'),  # (planificador, logistica)
    ('INVENTARIO', 'Inventario'),
    ('OPERADOR ACTIVACIONES', 'Operador Activaciones'),  # all ot
    # no filters (pool ips, netconect):
    ('OPERADOR NETWORKING', 'Operador Networking'),


    ('BODEGUERO', 'Bodeguero'),
    ('COORDINADOR_LOGISTICA', 'Coordinador Logistica'),
    ('COORDINADOR_VENTAS', 'Coordinador Ventas'),
    ('AUXILIAR', 'Auxiliar'),
    ('INVENTARIO GENERAL', 'Inventario General'),


    ('PRODUCTO', 'Producto'),
    ('TICKET', 'Ticket'),
)
