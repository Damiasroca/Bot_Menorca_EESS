# Button Labels
B1 = '💶 Per PREU'
B2 = '🚗🚜 Per COMBUSTIBLE'
B3 = '🏘 Per POBLE'
B4 = '👁‍🗨 +INFO'
B5 = '🔙 Enrrere'
B6 = '✅ 5 més barates'
B7 = '‼️ 5 més cares'
B8 = '🟢 Benzina 95 E5'
B9 = '⚫️ Gasoli A'
B10 = '🟡 Gasoli B'
B11 = '🟠 Gasoli Premium'
B12 = '⚪️ GLP'
B13 = 'MAÓ'
B14 = 'CIUTADELLA'
B15 = 'ALAIOR'
B16 = 'ES MERCADAL'
B17 = 'FERRERIES'
B18 = 'SANT LLUÍS'
B19 = 'FORNELLS'

# New feature buttons
B21 = '📊 Gràfics de preus'
B22 = '📍 Aprop meu'
B23 = '🔔 Alertes de preu'
B24 = '📅 Darrera setmana'
B25 = '📅 Darrer mes'
B26 = '🎯 5km radi'
B27 = '🎯 10km radi'
B28 = '✅ Crear alerta'
B29 = '❌ Eliminar alerta'
B30 = '📋 Les meves alertes'

# Town callback data prefixes
TOWN_PREFIX = 'town_'
# Fuel callback data prefixes
FUEL_PREFIX = 'fuel_'
# Chart callback data prefixes
CHART_PREFIX = 'chart_'
# Chart fuel selection prefix (to avoid conflicts with regular fuel handler)
CHART_FUEL_PREFIX = 'chartfuel_'
# Location callback data prefixes
LOCATION_PREFIX = 'location_'
# Alert callback data prefixes
ALERT_PREFIX = 'alert_'

# Messages
M_INSTRUCT = "▪️*Selecciona una opció :*"
M_CHART_SELECT = "📊 *Selecciona el combustible per veure l'evolució de preus:*"
M_LOCATION_REQUEST = "📍 *Comparteix la teva ubicació per trobar estacions prop teu*"
M_ALERT_SELECT = "🔔 *Gestiona les teves alertes de preu:*"

# Callback Data
(
    PREU, COMBUSTIBLE, POBLE, INFO, BARATES, CARES, INICI,
    CHARTS, LOCATION, ALERTS
) = map(str, range(10))

# Town callback data
P1 = f'{TOWN_PREFIX}MAO'
P2 = f'{TOWN_PREFIX}CIUTADELLA'
P3 = f'{TOWN_PREFIX}ALAIOR'
P4 = f'{TOWN_PREFIX}ES MERCADAL'
P5 = f'{TOWN_PREFIX}FERRERIES'
P6 = f'{TOWN_PREFIX}SANT LLUÍS'
P7 = f'{TOWN_PREFIX}FORNELLS'

# Fuel callback data
BENZINA = f'{FUEL_PREFIX}BENZINA'
GASOLIA = f'{FUEL_PREFIX}GASOLIA'
GASOLIB = f'{FUEL_PREFIX}GASOLIB'
GASOLIP = f'{FUEL_PREFIX}GASOLIP'
GLP = f'{FUEL_PREFIX}GLP'

# Chart callback data
CHART_BENZINA_7 = f'{CHART_PREFIX}BENZINA_7'
CHART_BENZINA_30 = f'{CHART_PREFIX}BENZINA_30'
CHART_GASOLIA_7 = f'{CHART_PREFIX}GASOLIA_7'
CHART_GASOLIA_30 = f'{CHART_PREFIX}GASOLIA_30'
CHART_GASOLIB_7 = f'{CHART_PREFIX}GASOLIB_7'
CHART_GASOLIB_30 = f'{CHART_PREFIX}GASOLIB_30'
CHART_GASOLIP_7 = f'{CHART_PREFIX}GASOLIP_7'
CHART_GASOLIP_30 = f'{CHART_PREFIX}GASOLIP_30'
CHART_GLP_7 = f'{CHART_PREFIX}GLP_7'
CHART_GLP_30 = f'{CHART_PREFIX}GLP_30'

# Location callback data
LOCATION_5KM = f'{LOCATION_PREFIX}5KM'
LOCATION_10KM = f'{LOCATION_PREFIX}10KM'

# Alert callback data
ALERT_CREATE = f'{ALERT_PREFIX}CREATE'
ALERT_REMOVE = f'{ALERT_PREFIX}REMOVE'
ALERT_LIST = f'{ALERT_PREFIX}LIST'
ALERT_CREATE_BENZINA = f'{ALERT_PREFIX}CREATE_BENZINA'
ALERT_CREATE_GASOLIA = f'{ALERT_PREFIX}CREATE_GASOLIA'
ALERT_CREATE_GASOLIB = f'{ALERT_PREFIX}CREATE_GASOLIB'
ALERT_CREATE_GASOLIP = f'{ALERT_PREFIX}CREATE_GASOLIP'
ALERT_CREATE_GLP = f'{ALERT_PREFIX}CREATE_GLP'

# Conversation States
NIVELL0, NIVELL1, NIVELL2, NIVELL3 = range(4) 