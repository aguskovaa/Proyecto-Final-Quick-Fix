# Configuración de Mercado Pago
MERCADO_PAGO_CONFIG = {
    "ACCESS_TOKEN": "APP_USR-XXXXXXXXXXXX-XXXXXXXXXXXX",  # TU ACCESS_TOKEN
    "MONEDA": "ARS",  # ARS, BRL, USD, etc.
    "WEBHOOK_URL": "https://tu-dominio.com/webhook/mercadopago",
    "SUCCESS_URL": "https://tu-dominio.com/pago/exitoso",
    "FAILURE_URL": "https://tu-dominio.com/pago/fallido",
    "PENDING_URL": "https://tu-dominio.com/pago/pendiente"
}

# Configuración de la aplicación
APP_CONFIG = {
    "DEBUG": True,
    "PUERTO": 5000,
    "HOST": "0.0.0.0"
}