# Configuration and Constants for Menorca Fuel Price Telegram Bot
# This file contains all user-facing strings, button labels, and location data

# ===============================
# MUNICIPALITIES (Administrative Regions)
# ===============================
# The primary dictionary for municipalities.
# Key: Official government IDMunicipio string.
# Value: Dictionary with user-facing display name.
# 'FORNELLS' uses a custom key for our specific correction rule.
MUNICIPALITIES = {
    '829': {'display_name': 'Maó'},
    '810': {'display_name': 'Ciutadella'},
    '794': {'display_name': 'Alaior'},
    '832': {'display_name': 'Es Mercadal'},
    '819': {'display_name': 'Ferreries'},
    '848': {'display_name': 'Sant Lluís'},
    '666': {'display_name': 'Fornells', 'is_custom': True}
}

# Helper function to safely get display names
def get_municipality_display_name(id_municipality):
    """Get user-friendly municipality name from its ID with fallback."""
    try:
        return MUNICIPALITIES.get(id_municipality, {}).get('display_name', id_municipality)
    except:
        return id_municipality

# ===============================
# FUEL TYPES
# Maps internal names to display names and database column names
# ===============================
FUEL_TYPES = {
    'GASOLINA_95_E5': {
        'display_name': 'Benzina 95 E5',
        'column': 'Precio_Gasolina_95_E5',
        'emoji': '🟢'
    },
    'GASOLINA_95_E5_PREMIUM': {
        'display_name': 'Benzina 95 E5 Premium',
        'column': 'Precio_Gasolina_95_E5_Premium',
        'emoji': '🌟'
    },
    'GASOLEO_A': {
        'display_name': 'Gasoli A',
        'column': 'Precio_Gasoleo_A',
        'emoji': '⚫️'
    },
    'GASOLEO_B': {
        'display_name': 'Gasoli B',
        'column': 'Precio_Gasoleo_B',
        'emoji': '🟡'
    },
    'GASOLEO_PREMIUM': {
        'display_name': 'Gasoli Premium',
        'column': 'Precio_Gasoleo_Premium',
        'emoji': '🟠'
    },
    'GLP': {
        'display_name': 'GLP',
        'column': 'Precio_Gases_Licuados_del_petroleo',
        'emoji': '⚪️'
    }
}

# ===============================
# BUTTON LABELS (User Interface)
# ===============================

# Main menu buttons
B1 = '💶 Per PREU'
B2 = '🚗🚜 Per COMBUSTIBLE'
B3 = '🏘 Per MUNICIPI'
B4 = '👁‍🗨 +INFO'
B5 = '🔙 Enrrere'

# Price menu buttons
B6 = '✅ 5 més barates'
B7 = '‼️ 5 més cares'

# Fuel type buttons
B8 = f"{FUEL_TYPES['GASOLINA_95_E5']['emoji']} {FUEL_TYPES['GASOLINA_95_E5']['display_name']}"
B9 = f"{FUEL_TYPES['GASOLINA_95_E5_PREMIUM']['emoji']} {FUEL_TYPES['GASOLINA_95_E5_PREMIUM']['display_name']}"
B10 = f"{FUEL_TYPES['GASOLEO_A']['emoji']} {FUEL_TYPES['GASOLEO_A']['display_name']}"
B11 = f"{FUEL_TYPES['GASOLEO_B']['emoji']} {FUEL_TYPES['GASOLEO_B']['display_name']}"
B12 = f"{FUEL_TYPES['GASOLEO_PREMIUM']['emoji']} {FUEL_TYPES['GASOLEO_PREMIUM']['display_name']}"
B13 = f"{FUEL_TYPES['GLP']['emoji']} {FUEL_TYPES['GLP']['display_name']}"

# Municipality buttons
B14 = get_municipality_display_name('829') # Maó
B15 = get_municipality_display_name('810') # Ciutadella
B16 = get_municipality_display_name('794') # Alaior
B17 = get_municipality_display_name('832') # Es Mercadal
B18 = get_municipality_display_name('819') # Ferreries
B19 = get_municipality_display_name('848') # Sant Lluís
B20 = get_municipality_display_name('666') # Fornells (Custom)

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

# Admin buttons
B_ADMIN_STATS = '📊 Estadístiques'
B_ADMIN_USERS = '👥 Usuaris'
B_ADMIN_BROADCAST = '📢 Difusió'
B_ADMIN_HEALTH = '🏥 Salut del sistema'

# ===============================
# MESSAGES (User Interface Text)
# ===============================

# Main messages
M_INSTRUCT = "▪️*Selecciona una opció:*"
M_WELCOME = "Benvingut *{}*.\nMés ⛽️ per menys 💶!\nPreus actualitzats cada 10 minuts."
M_PRICE_SELECT = "*SELECCIONA:*"
M_FUEL_SELECT = "*SELECCIONA EL COMBUSTIBLE:*"
M_MUNICIPALITY_SELECT = "*SELECCIONA EL MUNICIPI:*"

# Feature-specific messages
M_CHART_SELECT = "📊 *Selecciona el combustible per veure l'evolució de preus:*"
M_LOCATION_REQUEST = "📍 *Comparteix la teva ubicació per trobar estacions prop teu*"
M_ALERT_SELECT = "🔔 *Gestiona les teves alertes de preu:*"
M_ALERT_FUEL_SELECT = "🔔 *Selecciona el combustible per l'alerta:*"
M_ALERT_MUNICIPALITY_SELECT = "🔔 *Selecciona el municipi per l'alerta:*"
M_ALERT_PRICE_INPUT = "🔔 *Introdueix el preu objectiu (exemple: 1.45):*"
M_ALERT_CREATED = "✅ *Alerta creada!*\nRebràs una notificació quan el preu baixi de {}€/L"
M_ALERT_UPDATED = "✅ *Alerta actualitzada!*\nRebràs una notificació quan el preu baixi de {}€/L"
M_ALERT_REMOVED = "❌ *Alerta eliminada!*"
M_ALERT_NOT_FOUND = "❌ *No s'ha trobat l'alerta per eliminar.*"
M_ALERT_TRIGGERED = "🔔 *ALERTA DE PREU!*\n{} a {} ha baixat a {}€/L al municipi de {}!\n\n{}\n\n⚠️ *Aquesta alerta s'ha desactivat automàticament.* Si vols continuar rebent alertes per aquest combustible, crea una nova alerta."

# Info messages
M_INFO = ("Dades extretes de *Ministerio de Industria, Comercio y Turismo*.\n"
          "S'ha comprovat que algunes dades d'ubicació estan malament o no són prou precises.\n"
          "Les dades errònies han estat notificades.\n\n"
          "*Última actualització de preus:* {}\n\n"
          "Escrit per Damià Sintes.\n"
          "Codi a [GitHub](https://github.com/Damiasroca/Bot_Menorca_EESS)")

# Error messages
M_ERROR_GENERAL = "❌ S'ha produït un error. Torna-ho a provar."
M_ERROR_NO_DATA = "😨❌ No disponible en aquests moments"
M_ERROR_INVALID_PRICE = "❌ Preu no vàlid. Introdueix un número (exemple: 1.45)"
M_ERROR_NO_LOCATION = "📍 Comparteix la teva ubicació primer"

# Admin messages
M_ADMIN_ONLY = "❌ Aquesta funcionalitat només està disponible per administradors."
M_ADMIN_STATS = "📊 *Estadístiques del Bot*\n\nUsuaris totals: {}\nUsuaris actius: {}\nInteraccions avui: {}\nAlertes actives: {}"
M_ADMIN_BROADCAST_PROMPT = "📢 *Difusió de missatge*\n\nEscriu el missatge que vols enviar a tots els usuaris:"
M_ADMIN_BROADCAST_SENT = "📢 *Missatge enviat a {} usuaris*"

# ===============================
# CALLBACK DATA CONSTANTS
# ===============================

# Main conversation states
NIVELL0, NIVELL1, NIVELL2, NIVELL3, NIVELL4 = range(5)

# Alert conversation states
ALERT_FUEL_SELECT, ALERT_MUNICIPALITY_SELECT, ALERT_PRICE_INPUT = range(10, 13)

# Main callback data
PREU, COMBUSTIBLE, POBLE, INFO, BARATES, CARES, INICI = map(str, range(7))
CHARTS, LOCATION, ALERTS = map(str, range(20, 23))

# Callback data prefixes
TOWN_PREFIX = 'town_'
FUEL_PREFIX = 'fuel_'
CHART_PREFIX = 'chart_'
CHART_FUEL_PREFIX = 'chartfuel_'
LOCATION_PREFIX = 'location_'
ALERT_PREFIX = 'alert_'
ADMIN_PREFIX = 'admin_'

# Municipality callback data
MUNICIPIS_CALLBACK = {
    '829': f'{TOWN_PREFIX}829',       # Maó
    '810': f'{TOWN_PREFIX}810',       # Ciutadella
    '794': f'{TOWN_PREFIX}794',       # Alaior
    '832': f'{TOWN_PREFIX}832',       # Es Mercadal
    '819': f'{TOWN_PREFIX}819',       # Ferreries
    '848': f'{TOWN_PREFIX}848',       # Sant Lluís
    '666': f'{TOWN_PREFIX}666'        # Fornells (Custom)
}

# Fuel callback data
FUEL_CALLBACK = {
    'GASOLINA_95_E5': f'{FUEL_PREFIX}GASOLINA_95_E5',
    'GASOLINA_95_E5_PREMIUM': f'{FUEL_PREFIX}GASOLINA_95_E5_PREMIUM',
    'GASOLEO_A': f'{FUEL_PREFIX}GASOLEO_A',
    'GASOLEO_B': f'{FUEL_PREFIX}GASOLEO_B',
    'GASOLEO_PREMIUM': f'{FUEL_PREFIX}GASOLEO_PREMIUM',
    'GLP': f'{FUEL_PREFIX}GLP'
}

# Location callback data
LOCATION_5KM = f'{LOCATION_PREFIX}5KM'
LOCATION_10KM = f'{LOCATION_PREFIX}10KM'

# Alert callback data
ALERT_CREATE = f'{ALERT_PREFIX}CREATE'
ALERT_REMOVE = f'{ALERT_PREFIX}REMOVE'
ALERT_LIST = f'{ALERT_PREFIX}LIST'
ALERT_DELETE = f'{ALERT_PREFIX}DELETE'

# Admin callback data
ADMIN_STATS = f'{ADMIN_PREFIX}STATS'
ADMIN_USERS = f'{ADMIN_PREFIX}USERS'
ADMIN_BROADCAST = f'{ADMIN_PREFIX}BROADCAST'
ADMIN_HEALTH = f'{ADMIN_PREFIX}HEALTH'

# ===============================
# PAGINATION SETTINGS
# ===============================
RESULTS_PER_PAGE = 5
MAX_MUNICIPALITIES_PER_ROW = 3

# ===============================
# DEFAULT SETTINGS
# ===============================
DEFAULT_FUEL_TYPE = 'GASOLINA_95_E5'
DEFAULT_CHART_DAYS = 7
DEFAULT_LOCATION_RADIUS = 10
MAX_ALERT_PRICE = 3.0
MIN_ALERT_PRICE = 0.5 