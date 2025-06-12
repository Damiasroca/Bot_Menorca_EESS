# Main Telegram Bot Application for Menorca Fuel Prices
# Following the architecture described in technical_description.txt

import os
import sys
import logging
import datetime
from uuid import uuid4
from functools import wraps

from telegram.ext import (Application, CommandHandler, ConversationHandler, 
                         CallbackQueryHandler, CallbackContext, MessageHandler, 
                         filters, InlineQueryHandler, PicklePersistence)
from telegram import (InlineKeyboardMarkup, InlineKeyboardButton, Update, 
                     InlineQueryResultArticle, InputTextMessageContent, 
                     KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.constants import ParseMode

# Import our modules
import secret
from data_manager_menorca import menorca_data_manager
from constants_menorca import *
from constants_menorca import MUNICIPALITIES, get_municipality_display_name

def create_back_to_main_keyboard():
    """Create a consistent keyboard with back to main menu button."""
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🏠 Menú Principal", callback_data=str(INICI))
    ]])

def validate_fuel_type(fuel_type):
    """Validate that a fuel type exists in the database mapping."""
    return fuel_type in FUEL_TYPES

def validate_municipality(id_municipality):
    """Validate that a municipality ID exists."""
    return id_municipality in MUNICIPALITIES or id_municipality is None

def get_valid_fuel_types():
    """Get list of valid fuel type keys."""
    return list(FUEL_TYPES.keys())

def get_available_fuel_types_for_municipality(id_municipality):
    """Get fuel types that are actually available in stations for a specific municipality."""
    try:
        if not id_municipality:
            logger.error("get_available_fuel_types_for_municipality received a None ID")
            return []
        
        # Get stations for the municipality using the unique ID
        stations_df = menorca_data_manager.get_stations_by_municipality(id_municipality)
        
        if stations_df.empty:
            logger.warning(f"No stations found for municipality ID: {id_municipality}")
            return []
        
        available_fuel_types = []
        
        # Check each fuel type to see if it exists in any station in this municipality
        for fuel_key, fuel_info in FUEL_TYPES.items():
            column_name = fuel_info['column']
            
            # Check if any station in this municipality has this fuel type with valid price
            if column_name in stations_df.columns:
                valid_prices = stations_df[column_name].dropna()
                valid_prices = valid_prices[valid_prices > 0]
                
                if not valid_prices.empty:
                    available_fuel_types.append(fuel_key)
        
        municipality_display_name = get_municipality_display_name(id_municipality)
        logger.info(f"Municipality {municipality_display_name} (ID: {id_municipality}): Available fuel types: {available_fuel_types}")
        return available_fuel_types
        
    except Exception as e:
        logger.error(f"Error getting available fuel types for municipality ID {id_municipality}: {e}", exc_info=True)
        # Fallback to all fuel types if there's an error
        return list(FUEL_TYPES.keys())

def debug_municipality_mapping():
    """Debug function to verify municipality mappings work correctly."""
    logger.info("=== Municipality Mapping Debug ===")
    for id_municipality, muni_data in MUNICIPALITIES.items():
        logger.info(f"ID: '{id_municipality}' -> Name: '{muni_data['display_name']}'")
        # Test the function
        try:
            available_fuels = get_available_fuel_types_for_municipality(id_municipality)
            logger.info(f"  Available fuels: {available_fuels}")
        except Exception as e:
            logger.error(f"  Error: {e}")
    logger.info("=== End Municipality Mapping Debug ===")

# Setup logging following technical description pattern
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Console handler
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(log_formatter)
logger.addHandler(stream_handler)

# File handler
try:
    log_file_path = "logs/main_bot_menorca.log"
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)
    logger.info(f"Logging to {log_file_path}")
except (OSError, IOError) as e:
    logger.warning(f"Could not set up file logging to {log_file_path}: {e}")

def admin_required(func):
    """Decorator to restrict access to admin users only."""
    @wraps(func)
    async def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in secret.secret.get('admin_user_ids', []):
            if update.callback_query:
                await update.callback_query.answer(M_ADMIN_ONLY, show_alert=True)
            else:
                await update.message.reply_text(M_ADMIN_ONLY, reply_markup=create_back_to_main_keyboard())
            return ConversationHandler.END
        return await func(update, context, *args, **kwargs)
    return wrapper

def error_handler(func):
    """Error handling decorator following technical description pattern."""
    @wraps(func)
    async def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        try:
            # Track user interaction
            track_user_from_update(update)
            return await func(update, context, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in handler {func.__name__}: {e}", exc_info=True)
            if query := update.callback_query:
                await query.answer(text=M_ERROR_GENERAL, show_alert=True)
            elif update.message:
                await update.message.reply_text(M_ERROR_GENERAL, reply_markup=create_back_to_main_keyboard())
            return ConversationHandler.END
    return wrapper

def track_user_from_update(update: Update):
    """Extract user info from update and track interaction."""
    try:
        user = None
        if update.message:
            user = update.message.from_user
        elif update.callback_query:
            user = update.callback_query.from_user
        elif update.inline_query:
            user = update.inline_query.from_user
            
        if user:
            menorca_data_manager.track_user_interaction(
                user_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                language_code=user.language_code
            )
    except Exception as e:
        logger.error(f"Error tracking user interaction: {e}")

# ===============================
# UTILITY FUNCTIONS
# ===============================

def format_station_message(station, show_fuels=None):
    """Format a station message with specified fuel types, following Tenerife bot style."""
    if show_fuels is None:
        # Default fuels to show - use all available fuel types
        show_fuels = list(FUEL_TYPES.keys())
    
    # Create Google Maps link with proper fallback
    if station.get('Latitud') and station.get('Longitud_WGS84'):
        lat = str(station['Latitud']).replace(',', '.')
        lon = str(station['Longitud_WGS84']).replace(',', '.')
        maps_link = f'https://www.google.com/maps/@{lat},{lon},20z'
        header = f"🔸*{station.get('Rotulo', 'Desconegut')}*\n[{station.get('Direccion', 'Adreça desconeguda')}]({maps_link})"
    else:
        header = f"🔸*{station.get('Rotulo', 'Desconegut')}*\n{station.get('Direccion', 'Adreça desconeguda')}"
    
    # Add location info
    if station.get('Localidad'):
        header += f"\n📍 {station['Localidad']}"
    
    # Add fuel prices using FUEL_TYPES dictionary
    fuel_lines = []
    for fuel_key in show_fuels:
        if fuel_key in FUEL_TYPES:
            # Map to the actual database column name (uppercase format)
            fuel_info = FUEL_TYPES[fuel_key]
            
            # Convert lowercase column name to database format
            if fuel_key == 'GASOLINA_95_E5':
                column_name = 'Precio_Gasolina_95_E5'
            elif fuel_key == 'GASOLINA_95_E5_PREMIUM':
                column_name = 'Precio_Gasolina_95_E5_Premium'
            elif fuel_key == 'GASOLEO_A':
                column_name = 'Precio_Gasoleo_A'
            elif fuel_key == 'GASOLEO_B':
                column_name = 'Precio_Gasoleo_B'
            elif fuel_key == 'GASOLEO_PREMIUM':
                column_name = 'Precio_Gasoleo_Premium'
            elif fuel_key == 'GLP':
                column_name = 'Precio_Gases_Licuados_del_petroleo'
            else:
                continue  # Skip unknown fuel types
            
            # Check if station has this fuel type with valid price
            if column_name in station and station[column_name] is not None and station[column_name] > 0:
                fuel_display = fuel_info['display_name']
                fuel_emoji = fuel_info['emoji']
                price = station[column_name]
                fuel_lines.append(f"{fuel_emoji} {fuel_display}: *{price}€*")
    
    # Add fuel prices to message
    if fuel_lines:
        header += "\n" + "\n".join(fuel_lines)
    
    # Add opening hours if available - check multiple possible column names
    horario_value = None
    possible_horario_keys = ['Horario', 'horario', 'HORARIO', 'schedule', 'opening_hours']
    
    for key in possible_horario_keys:
        if key in station and station[key] is not None:
            value = str(station[key]).strip()
            if value and value.lower() not in ['null', 'none', 'nan', '']:
                horario_value = value
                break
    
    if horario_value:
        header += f"\n⏰ {horario_value}"
    
    # Debug: Log what we found (remove this in production)
    station_name = station.get('Rotulo', 'Unknown')
    logger.debug(f"Station {station_name}: Horario = '{horario_value}', Available keys with 'horario': {[k for k in station.keys() if 'horario' in k.lower()]}")
    
    return header

def get_municipality_buttons(page=0):
    """Generate municipality buttons with pagination."""
    municipalities = list(MUNICIPALITIES.items())
    start_idx = page * (MAX_MUNICIPALITIES_PER_ROW * 3)  # 3 rows per page
    end_idx = start_idx + (MAX_MUNICIPALITIES_PER_ROW * 3)
    
    buttons = []
    current_row = []
    
    for i, (id_municipality, muni_data) in enumerate(municipalities[start_idx:end_idx]):
        # Use display name for button text but keep ID for callback data
        display_name = muni_data['display_name']
        
        button = InlineKeyboardButton(display_name, callback_data=MUNICIPIS_CALLBACK[id_municipality])
        current_row.append(button)
        
        if len(current_row) == MAX_MUNICIPALITIES_PER_ROW or i == len(municipalities[start_idx:end_idx]) - 1:
            buttons.append(current_row)
            current_row = []
    
    # Add navigation buttons if needed
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Anterior", callback_data=f"page_{page-1}"))
    if end_idx < len(municipalities):
        nav_buttons.append(InlineKeyboardButton("Següent ➡️", callback_data=f"page_{page+1}"))
    
    if nav_buttons:
        buttons.append(nav_buttons)
    
    # Back button
    buttons.append([InlineKeyboardButton(B5, callback_data=str(INICI))])
    
    return buttons

# ===============================
# MAIN CONVERSATION HANDLERS
# ===============================

@error_handler
async def start(update: Update, context: CallbackContext):
    """Start command handler following technical description pattern."""
    user = update.message.from_user
    welcome_message = M_WELCOME.format(user.username or user.first_name or "usuari")
    
    await update.message.reply_text(
        welcome_message, 
        parse_mode=ParseMode.MARKDOWN, 
        disable_web_page_preview=True
    )

    # Main menu following technical description structure
    keyboard = [
        [InlineKeyboardButton(B1, callback_data=str(PREU)),
         InlineKeyboardButton(B2, callback_data=str(COMBUSTIBLE))],
        [InlineKeyboardButton(B3, callback_data=str(POBLE)),
         InlineKeyboardButton(B4, callback_data=str(INFO))],
        [InlineKeyboardButton(B21, callback_data=str(CHARTS)),
         InlineKeyboardButton(B22, callback_data=str(LOCATION))],
        [InlineKeyboardButton(B23, callback_data=str(ALERTS))]
    ]

    await update.message.reply_text(
        M_INSTRUCT,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return NIVELL1

@error_handler
async def start_over(update: Update, context: CallbackContext):
    """Return to main menu - handles both callback queries and text messages."""
    # Handle both callback queries and regular messages
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        
        # Check if the message has text that can be edited
        # If it's a photo message (like chart), we need to send a new message instead
        if query.message.text:
            edit_message = True
        else:
            edit_message = False
    else:
        # Handle regular text message (from ReplyKeyboardMarkup)
        edit_message = False

    keyboard = [
        [InlineKeyboardButton(B1, callback_data=str(PREU)),
         InlineKeyboardButton(B2, callback_data=str(COMBUSTIBLE))],
        [InlineKeyboardButton(B3, callback_data=str(POBLE)),
         InlineKeyboardButton(B4, callback_data=str(INFO))],
        [InlineKeyboardButton(B21, callback_data=str(CHARTS)),
         InlineKeyboardButton(B22, callback_data=str(LOCATION))],
        [InlineKeyboardButton(B23, callback_data=str(ALERTS))]
    ]
    
    if edit_message:
        # Edit existing text message
        await update.callback_query.edit_message_text(
            M_INSTRUCT,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        # Send new message (for photo messages, regular messages, etc.)
        if update.callback_query:
            # This is a callback query from a non-text message (like photo)
            await context.bot.send_message(
                chat_id=update.callback_query.message.chat_id,
                text=M_INSTRUCT,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            # This is a regular text message
            await update.message.reply_text(
                M_INSTRUCT,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            # Send a minimal message to remove the custom keyboard
            await context.bot.send_message(
                chat_id=update.message.chat_id,
                text="🏠",
                reply_markup=ReplyKeyboardRemove()
            )
    
    return NIVELL1

# ===============================
# PRICE QUERY HANDLERS
# ===============================

@error_handler
async def price_menu(update: Update, context: CallbackContext):
    """Price selection menu."""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton(B6, callback_data=str(BARATES)),
         InlineKeyboardButton(B7, callback_data=str(CARES))],
        [InlineKeyboardButton(B5, callback_data=str(INICI))]
    ]
    
    await query.edit_message_text(
        M_PRICE_SELECT,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return NIVELL2

@error_handler
async def cheapest_stations(update: Update, context: CallbackContext):
    """Show 5 cheapest stations following technical description logic."""
    query = update.callback_query
    await query.answer()
    
    # Get cheapest stations for default fuel type
    stations_df = menorca_data_manager.get_stations_by_fuel_ascending(DEFAULT_FUEL_TYPE, 5)
    
    if stations_df.empty:
        message = M_ERROR_NO_DATA
    else:
        fuel_display = FUEL_TYPES[DEFAULT_FUEL_TYPE]['display_name']
        message = f"🏆 *5 més barates - {fuel_display}*\n\n"
        
        messages = []
        for _, station in stations_df.iterrows():
            # Show main fuel types for comparison
            station_msg = format_station_message(
                station.to_dict(), 
                ['GASOLINA_95_E5', 'GASOLEO_A', 'GASOLINA_95_E5_PREMIUM']
            )
            messages.append(station_msg)
        message += "\n\n".join(messages)
    
    keyboard = [[InlineKeyboardButton("🏠 Menú Principal", callback_data=str(INICI))]]
    
    await query.edit_message_text(
        message,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return NIVELL1

@error_handler
async def most_expensive_stations(update: Update, context: CallbackContext):
    """Show 5 most expensive stations."""
    query = update.callback_query
    await query.answer()
    
    # Get most expensive stations for default fuel type
    stations_df = menorca_data_manager.get_stations_by_fuel_descending(DEFAULT_FUEL_TYPE, 5)
    
    if stations_df.empty:
        message = M_ERROR_NO_DATA
    else:
        fuel_display = FUEL_TYPES[DEFAULT_FUEL_TYPE]['display_name']
        message = f"💸 *5 més cares - {fuel_display}*\n\n"
        
        messages = []
        for _, station in stations_df.iterrows():
            # Show main fuel types for comparison
            station_msg = format_station_message(
                station.to_dict(), 
                ['GASOLINA_95_E5', 'GASOLEO_A', 'GASOLINA_95_E5_PREMIUM']
            )
            messages.append(station_msg)
        message += "\n\n".join(messages)
    
    keyboard = [[InlineKeyboardButton("🏠 Menú Principal", callback_data=str(INICI))]]
    
    await query.edit_message_text(
        message,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return NIVELL1

# ===============================
# FUEL TYPE HANDLERS
# ===============================

@error_handler
async def fuel_type_menu(update: Update, context: CallbackContext):
    """Fuel type selection menu."""
    query = update.callback_query
    await query.answer()
    
    keyboard = []
    for fuel_key, fuel_data in FUEL_TYPES.items():
        button_text = f"{fuel_data['emoji']} {fuel_data['display_name']}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=FUEL_CALLBACK[fuel_key])])
    
    keyboard.append([InlineKeyboardButton(B5, callback_data=str(INICI))])
    
    await query.edit_message_text(
        M_FUEL_SELECT,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return NIVELL2

@error_handler
async def fuel_type_info(update: Update, context: CallbackContext):
    """Show cheapest stations for specific fuel type."""
    query = update.callback_query
    await query.answer()
    
    # Parse fuel type from callback data
    fuel_type = query.data.split('_', 1)[1]  # Remove FUEL_PREFIX
    
    if fuel_type not in FUEL_TYPES:
        await query.edit_message_text(M_ERROR_GENERAL, reply_markup=create_back_to_main_keyboard())
        return NIVELL1
    
    # Get cheapest stations for this fuel type
    stations_df = menorca_data_manager.get_stations_by_fuel_ascending(fuel_type, 5)
    
    if stations_df.empty:
        message = M_ERROR_NO_DATA
    else:
        fuel_name = FUEL_TYPES[fuel_type]['display_name']
        message = f"🏆 *5 més barates - {fuel_name}*\n\n"
        
        messages = []
        for _, station in stations_df.iterrows():
            # Show the specific fuel type requested plus common ones for comparison
            show_fuels = [fuel_type, 'GASOLINA_95_E5', 'GASOLEO_A'] if fuel_type not in ['GASOLINA_95_E5', 'GASOLEO_A'] else [fuel_type]
            station_msg = format_station_message(station.to_dict(), show_fuels)
            messages.append(station_msg)
        message += "\n\n".join(messages)
    
    keyboard = [[InlineKeyboardButton("🏠 Menú Principal", callback_data=str(INICI))]]
    
    await query.edit_message_text(
        message,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return NIVELL1

# ===============================
# MUNICIPALITY HANDLERS
# ===============================

@error_handler
async def municipality_menu(update: Update, context: CallbackContext):
    """Municipality selection menu with pagination."""
    query = update.callback_query
    await query.answer()
    
    # Handle pagination
    if query.data.startswith('page_'):
        page = int(query.data.split('_')[1])
    else:
        page = 0
    
    buttons = get_municipality_buttons(page)
    
    await query.edit_message_text(
        M_MUNICIPALITY_SELECT,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    return NIVELL2

@error_handler
async def municipality_info(update: Update, context: CallbackContext):
    """Show stations in a specific municipality following technical description pattern."""
    query = update.callback_query
    await query.answer()
    
    # Parse municipality ID from callback data
    id_municipality = query.data.split('_', 1)[1]  # Remove TOWN_PREFIX
    
    if not validate_municipality(id_municipality):
        await query.edit_message_text(M_ERROR_GENERAL, reply_markup=create_back_to_main_keyboard())
        return NIVELL1
    
    # Get stations for this municipality
    stations_df = menorca_data_manager.get_stations_by_municipality(id_municipality)
    
    if stations_df.empty:
        message = M_ERROR_NO_DATA
    else:
        # Use display name for user-facing text
        municipality_display_name = get_municipality_display_name(id_municipality)
        
        message = f"⛽️ *Estacions a {municipality_display_name}*\n\n"
        
        messages = []
        for _, station in stations_df.iterrows():
            # Show all main fuel types for comprehensive view
            station_msg = format_station_message(
                station.to_dict(),
                ['GASOLINA_95_E5', 'GASOLINA_95_E5_PREMIUM', 'GASOLEO_A', 'GASOLEO_PREMIUM', 'GLP']
            )
            messages.append(station_msg)
        message += "\n\n".join(messages)
    
    # Add create alert button using display name
    municipality_display_name = get_municipality_display_name(id_municipality)
    
    keyboard = [
        [InlineKeyboardButton(f"🔔 Crear alerta - {municipality_display_name}", 
                            callback_data=f"{ALERT_PREFIX}CREATE_{id_municipality}")],
        [InlineKeyboardButton("🏠 Menú Principal", callback_data=str(INICI))]
    ]
    
    await query.edit_message_text(
        message,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return NIVELL1

# ===============================
# LOCATION HANDLERS
# ===============================

@error_handler
async def location_search(update: Update, context: CallbackContext):
    """Location search menu."""
    query = update.callback_query
    await query.answer()
    
    # Request location
    keyboard = [
        [KeyboardButton("📍 Compartir ubicació", request_location=True)],
        [KeyboardButton("🔙 Menú principal")]
    ]
    
    await query.edit_message_text(M_LOCATION_REQUEST, parse_mode=ParseMode.MARKDOWN)
    
    # Send new message with location keyboard
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text="👇 Prem el botó per compartir la teva ubicació:",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    
    return NIVELL2

@error_handler
async def handle_location(update: Update, context: CallbackContext):
    """Handle received location and show nearby stations."""
    if not update.message.location:
        await update.message.reply_text(
            M_ERROR_NO_LOCATION,
            reply_markup=ReplyKeyboardRemove()
        )
        return NIVELL1
    
    user_lat = update.message.location.latitude
    user_lon = update.message.location.longitude
    
    # Remove location keyboard immediately
    await update.message.reply_text(
        "📍 Ubicació rebuda! Cercant estacions properes...",
        reply_markup=ReplyKeyboardRemove()
    )
    
    # Find nearby stations
    nearby_stations = menorca_data_manager.find_stations_near_location(
        user_lat, user_lon, DEFAULT_LOCATION_RADIUS
    )
    
    if not nearby_stations:
        message = f"😞 No s'han trobat estacions en un radi de {DEFAULT_LOCATION_RADIUS}km"
        buttons = [
            [InlineKeyboardButton("🏠 Menú Principal", callback_data=str(INICI))]
        ]
    else:
        message = f"🎯 *Estacions properes (radi {DEFAULT_LOCATION_RADIUS}km)*\n\n"
        messages = []
        
        for station in nearby_stations[:5]:  # Show top 5
            # Show main fuel types for nearby stations
            station_msg = format_station_message(
                station,
                ['GASOLINA_95_E5', 'GASOLEO_A', 'GASOLINA_95_E5_PREMIUM']
            )
            station_msg += f"\n📏 Distància: *{station['distance']}km*"
            messages.append(station_msg)
        
        message += "\n\n".join(messages)
        
        buttons = [
            [InlineKeyboardButton("🏠 Menú Principal", callback_data=str(INICI))]
        ]
    
    await update.message.reply_text(
        message,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    
    return NIVELL1

# ===============================
# PRICE CHARTS HANDLERS
# ===============================

@error_handler
async def price_charts_menu(update: Update, context: CallbackContext):
    """Price charts menu."""
    query = update.callback_query
    await query.answer()
    
    keyboard = []
    for fuel_key, fuel_data in FUEL_TYPES.items():
        button_text = f"{fuel_data['emoji']} {fuel_data['display_name']}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"{CHART_FUEL_PREFIX}{fuel_key}")])
    
    keyboard.append([InlineKeyboardButton(B5, callback_data=str(INICI))])
    
    await query.edit_message_text(
        M_CHART_SELECT,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return NIVELL2

@error_handler
async def chart_period_selection(update: Update, context: CallbackContext):
    """Chart period selection."""
    query = update.callback_query
    await query.answer()
    
    # Parse fuel type from callback data
    fuel_type = query.data.split('_', 1)[1]  # Remove CHART_FUEL_PREFIX
    
    # Store fuel type in context
    context.user_data['chart_fuel'] = fuel_type
    
    fuel_name = FUEL_TYPES[fuel_type]['display_name']
    
    keyboard = [
        [InlineKeyboardButton(B24, callback_data=f"{CHART_PREFIX}{fuel_type}_7"),
         InlineKeyboardButton(B25, callback_data=f"{CHART_PREFIX}{fuel_type}_30")],
        [InlineKeyboardButton("🏠 Menú Principal", callback_data=str(INICI))]
    ]
    
    await query.edit_message_text(
        f"📊 *{fuel_name} - Selecciona període:*",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return NIVELL2

@error_handler
async def generate_chart(update: Update, context: CallbackContext):
    """Generate and send price chart."""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text("📊 Generant gràfic... Espera un moment.")
    
    # Parse callback data - Handle fuel types with underscores like GASOLEO_A
    # Expected format: chart_FUEL_TYPE_DAYS (e.g., chart_GASOLEO_A_7, chart_GASOLINA_95_E5_30)
    callback_data = query.data
    
    # Remove the CHART_PREFIX first
    if callback_data.startswith(CHART_PREFIX):
        data_without_prefix = callback_data[len(CHART_PREFIX):]
    else:
        logger.error(f"Invalid callback data format: {callback_data}")
        await query.edit_message_text("❌ Error en el format de dades", reply_markup=create_back_to_main_keyboard())
        return NIVELL1
    
    # Split by underscore and find the last part (should be the days)
    parts = data_without_prefix.split('_')
    try:
        days = int(parts[-1])  # Last part should be the number of days
        fuel_type = '_'.join(parts[:-1])  # Everything except the last part is the fuel type
    except (ValueError, IndexError):
        logger.error(f"Could not parse days from callback data: {callback_data}")
        await query.edit_message_text("❌ Error en el format de dades", reply_markup=create_back_to_main_keyboard())
        return NIVELL1
    
    # Validate fuel type
    if fuel_type not in FUEL_TYPES:
        logger.error(f"Invalid fuel type: {fuel_type}")
        await query.edit_message_text("❌ Tipus de combustible no vàlid", reply_markup=create_back_to_main_keyboard())
        return NIVELL1
    
    logger.info(f"Generating chart for fuel_type='{fuel_type}', days={days}")
    
    # Generate chart
    chart_buffer = menorca_data_manager.generate_price_chart(fuel_type, days)
    
    if chart_buffer:
        chart_buffer.seek(0)
        fuel_name = FUEL_TYPES[fuel_type]['display_name']
        
        # Create keyboard for the chart message
        keyboard = [[InlineKeyboardButton("🏠 Menú Principal", callback_data=str(INICI))]]
        
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo=chart_buffer,
            caption=f"📊 Evolució preus {fuel_name} - Últims {days} dies",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        # Delete the "generating chart" message since we now have the chart with navigation
        await query.delete_message()
    else:
        await query.edit_message_text(
            "❌ No hi ha dades suficients per generar el gràfic",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Menú Principal", callback_data=str(INICI))]])
        )
    
    return NIVELL1

# ===============================
# PRICE ALERTS HANDLERS
# ===============================

@error_handler
async def price_alerts_menu(update: Update, context: CallbackContext):
    """Price alerts management menu."""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton(B28, callback_data=ALERT_CREATE)],
        [InlineKeyboardButton(B30, callback_data=ALERT_LIST),
         InlineKeyboardButton(B29, callback_data=ALERT_REMOVE)],
        [InlineKeyboardButton(B5, callback_data=str(INICI))]
    ]
    
    await query.edit_message_text(
        M_ALERT_SELECT,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return NIVELL2

@error_handler
async def create_alert_fuel_selection(update: Update, context: CallbackContext):
    """Create alert - fuel selection step."""
    query = update.callback_query
    await query.answer()
    
    keyboard = []
    for fuel_key, fuel_data in FUEL_TYPES.items():
        button_text = f"{fuel_data['emoji']} {fuel_data['display_name']}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"{ALERT_PREFIX}FUEL_{fuel_key}")])
    
    keyboard.append([InlineKeyboardButton("🏠 Menú Principal", callback_data=str(INICI))])
    
    await query.edit_message_text(
        M_ALERT_FUEL_SELECT,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ALERT_FUEL_SELECT

@error_handler
async def create_alert_municipality_selection(update: Update, context: CallbackContext):
    """Create alert - municipality selection step."""
    query = update.callback_query
    await query.answer()
    
    # Parse fuel type from callback data
    fuel_type = query.data.split('_', 2)[2]  # Remove ALERT_PREFIX and FUEL_
    
    # Validate fuel type
    if not validate_fuel_type(fuel_type):
        logger.error(f"Invalid fuel type in alert creation: {fuel_type}")
        await query.edit_message_text(
            "❌ Tipus de combustible no vàlid", 
            reply_markup=create_back_to_main_keyboard()
        )
        return NIVELL1
    
    context.user_data['alert_fuel'] = fuel_type
    
    keyboard = []
    for id_municipality, muni_data in MUNICIPALITIES.items():
        display_name = muni_data['display_name']
        
        keyboard.append([InlineKeyboardButton(
            display_name, 
            callback_data=f"{ALERT_PREFIX}MUNICIPALITY_{id_municipality}"
        )])
    
    # Add option for all municipalities
    keyboard.append([InlineKeyboardButton(
        "🏝️ Tota Menorca", 
        callback_data=f"{ALERT_PREFIX}MUNICIPALITY_ALL"
    )])
    keyboard.append([InlineKeyboardButton("🏠 Menú Principal", callback_data=str(INICI))])
    
    fuel_name = FUEL_TYPES[fuel_type]['display_name']
    await query.edit_message_text(
        f"🔔 *Alerta per {fuel_name}*\n\n{M_ALERT_MUNICIPALITY_SELECT}",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ALERT_MUNICIPALITY_SELECT

@error_handler
async def create_alert_price_input(update: Update, context: CallbackContext):
    """Create alert - price input step."""
    query = update.callback_query
    await query.answer()
    
    # Parse municipality from callback data
    id_municipality = query.data.split('_', 2)[2]  # Remove ALERT_PREFIX and MUNICIPALITY_
    if id_municipality == 'ALL':
        id_municipality = None
    
    context.user_data['alert_municipality'] = id_municipality
    
    fuel_type = context.user_data.get('alert_fuel')
    fuel_name = FUEL_TYPES[fuel_type]['display_name']
    
    # Use display name for user-facing text
    if id_municipality:
        municipality_name = get_municipality_display_name(id_municipality)
    else:
        municipality_name = 'Tota Menorca'
    
    await query.edit_message_text(
        f"🔔 *Alerta per {fuel_name} a {municipality_name}*\n\n{M_ALERT_PRICE_INPUT}",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=create_back_to_main_keyboard()
    )
    
    return ALERT_PRICE_INPUT

@error_handler
async def handle_alert_price(update: Update, context: CallbackContext):
    """Handle price input for alert creation."""
    logger.info(f"Handling price input for alert creation. User: {update.message.from_user.id}")
    
    try:
        price_text = update.message.text.strip().replace(',', '.')
        price = float(price_text)
        logger.info(f"Parsed price: {price}")
        
        if price < MIN_ALERT_PRICE or price > MAX_ALERT_PRICE:
            logger.warning(f"Price {price} outside valid range ({MIN_ALERT_PRICE}-{MAX_ALERT_PRICE})")
            await update.message.reply_text(
                f"❌ El preu ha d'estar entre {MIN_ALERT_PRICE}€ i {MAX_ALERT_PRICE}€",
                reply_markup=create_back_to_main_keyboard()
            )
            return ALERT_PRICE_INPUT
            
    except ValueError as e:
        logger.error(f"Invalid price format: {update.message.text}, error: {e}")
        await update.message.reply_text(M_ERROR_INVALID_PRICE, reply_markup=create_back_to_main_keyboard())
        return ALERT_PRICE_INPUT
    
    # Create the alert
    user = update.message.from_user
    fuel_type = context.user_data.get('alert_fuel')
    id_municipality = context.user_data.get('alert_municipality')
    
    # Validate stored data
    if not fuel_type or not validate_fuel_type(fuel_type):
        logger.error(f"Invalid or missing fuel type in alert creation: {fuel_type}")
        await update.message.reply_text(
            "❌ Error: tipus de combustible no vàlid", 
            reply_markup=create_back_to_main_keyboard()
        )
        context.user_data.clear()
        return NIVELL1
    
    if not validate_municipality(id_municipality):
        logger.error(f"Invalid municipality in alert creation: {id_municipality}")
        await update.message.reply_text(
            "❌ Error: municipi no vàlid", 
            reply_markup=create_back_to_main_keyboard()
        )
        context.user_data.clear()
        return NIVELL1
    
    # Additional validation: check if the fuel type is actually available in this municipality
    if id_municipality:
        available_fuel_types = get_available_fuel_types_for_municipality(id_municipality)
        if fuel_type not in available_fuel_types:
            logger.error(f"Fuel type {fuel_type} not available in municipality {id_municipality}")
            municipality_display_name = get_municipality_display_name(id_municipality)
            fuel_display_name = FUEL_TYPES.get(fuel_type, {}).get('display_name', fuel_type)
            await update.message.reply_text(
                f"❌ {fuel_display_name} no està disponible a {municipality_display_name}",
                reply_markup=create_back_to_main_keyboard()
            )
            return NIVELL1
    
    logger.info(f"Creating alert - User: {user.id}, Fuel: {fuel_type}, Municipality ID: {id_municipality}, Price: {price}")
    
    success = menorca_data_manager.create_price_alert(
        user_id=user.id,
        username=user.username or user.first_name,
        fuel_type=fuel_type,
        price_threshold=price,
        id_municipality=id_municipality
    )
    
    if success:
        logger.info(f"Alert created successfully for user {user.id}")
        fuel_name = FUEL_TYPES[fuel_type]['display_name']
        # Use display name for user-facing text
        if id_municipality:
            municipality_name = get_municipality_display_name(id_municipality)
        else:
            municipality_name = 'Tota Menorca'
        
        message = M_ALERT_CREATED.format(price)
        message += f"\n\n📋 *Detalls:*\n"
        message += f"⛽️ Combustible: {fuel_name}\n"
        message += f"📍 Àmbit: {municipality_name}\n"
        message += f"🎯 Preu objectiu: {price}€/L"
        
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN, reply_markup=create_back_to_main_keyboard())
    else:
        logger.error(f"Failed to create alert for user {user.id}")
        await update.message.reply_text("❌ Error creant l'alerta. Torna-ho a provar.", reply_markup=create_back_to_main_keyboard())
    
    # Clear context
    context.user_data.clear()
    logger.info("Cleared user context data")
    return NIVELL1

@error_handler
async def list_user_alerts(update: Update, context: CallbackContext):
    """List user's active alerts."""
    query = update.callback_query
    await query.answer()
    
    user_alerts = menorca_data_manager.get_user_alerts(query.from_user.id)
    
    if user_alerts.empty:
        message = "📋 No tens alertes actives"
    else:
        message = "📋 *Les teves alertes actives:*\n\n"
        for _, alert in user_alerts.iterrows():
            # Handle unknown fuel types gracefully
            try:
                fuel_name = FUEL_TYPES[alert['fuel_type']]['display_name']
            except KeyError:
                # Fallback for unknown fuel types
                fuel_name = alert['fuel_type'].replace('_', ' ').title()
                logger.warning(f"Unknown fuel type in alert notification: {alert['fuel_type']}")
            
            # Use display name for user-facing text
            id_municipality = alert.get('id_municipality')
            if id_municipality:
                municipality_name = get_municipality_display_name(id_municipality)
            else:
                municipality_name = 'Tota Menorca'
            
            message += f"🔔 {fuel_name}\n"
            message += f"📍 {municipality_name}\n"
            message += f"🎯 Preu: {alert['price_threshold']}€/L\n"
            message += f"📅 Creada: {alert['created_at'].strftime('%d/%m/%Y')}\n\n"
    
    keyboard = [[InlineKeyboardButton("🏠 Menú Principal", callback_data=str(INICI))]]
    
    await query.edit_message_text(
        message,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return NIVELL1

@error_handler
async def remove_user_alerts(update: Update, context: CallbackContext):
    """Show user's alerts with delete buttons."""
    query = update.callback_query
    await query.answer()
    
    user_alerts = menorca_data_manager.get_user_alerts(query.from_user.id)
    
    if user_alerts.empty:
        message = "📋 No tens alertes per eliminar"
        keyboard = [[InlineKeyboardButton("🏠 Menú Principal", callback_data=str(INICI))]]
    else:
        message = "🗑️ *Selecciona l'alerta a eliminar:*\n\n"
        keyboard = []
        
        for idx, alert in user_alerts.iterrows():
            # Handle unknown fuel types gracefully
            try:
                fuel_name = FUEL_TYPES[alert['fuel_type']]['display_name']
            except KeyError:
                fuel_name = alert['fuel_type'].replace('_', ' ').title()
                logger.warning(f"Unknown fuel type in alert removal: {alert['fuel_type']}")
            
            # Use display name for user-facing text
            id_municipality = alert.get('id_municipality')
            if id_municipality:
                municipality_name = get_municipality_display_name(id_municipality)
            else:
                municipality_name = 'Tota Menorca'
            
            # Show alert details
            message += f"🔔 {fuel_name}\n"
            message += f"📍 {municipality_name}\n"
            message += f"🎯 Preu: {alert['price_threshold']}€/L\n"
            message += f"📅 Creada: {alert['created_at'].strftime('%d/%m/%Y')}\n\n"
            
            # Create unique identifier using fuel_type, id_municipality, and price
            # Format: FUEL_TYPE|ID_MUNICIPALITY|PRICE
            alert_identifier = f"{alert['fuel_type']}|{id_municipality if id_municipality else 'NULL'}|{alert['price_threshold']}"
            
            # Add delete button for this specific alert
            delete_button = InlineKeyboardButton(
                f"🗑️ Eliminar: {fuel_name} - {municipality_name}",
                callback_data=f"{ALERT_DELETE}_{alert_identifier}"
            )
            keyboard.append([delete_button])
        
        # Add back button
        keyboard.append([InlineKeyboardButton("🔙 Tornar", callback_data=str(ALERTS))])
        keyboard.append([InlineKeyboardButton("🏠 Menú Principal", callback_data=str(INICI))])
    
    await query.edit_message_text(
        message,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return NIVELL1

@error_handler
async def delete_specific_alert(update: Update, context: CallbackContext):
    """Delete a specific alert by identifier."""
    query = update.callback_query
    await query.answer()
    
    logger.info(f"🗑️ DELETE ALERT TRIGGERED - User: {query.from_user.id}, Callback data: {query.data}")
    
    try:
        # Parse alert identifier from callback data: alert_DELETE_FUEL|ID_MUNICIPALITY|PRICE
        callback_parts = query.data.split('_', 2)  # Split only on first 2 underscores
        if len(callback_parts) < 3:
            raise ValueError("Invalid callback data format")
        
        alert_identifier = callback_parts[2]  # Everything after alert_DELETE_
        logger.info(f"Parsed alert identifier: {alert_identifier}")
        
        # Parse the identifier: FUEL_TYPE|ID_MUNICIPALITY|PRICE
        identifier_parts = alert_identifier.split('|')
        if len(identifier_parts) != 3:
            raise ValueError("Invalid alert identifier format")
        
        fuel_type = identifier_parts[0]
        id_municipality = identifier_parts[1] if identifier_parts[1] != 'NULL' else None
        price_threshold = float(identifier_parts[2])
        
        logger.info(f"Attempting to delete alert: fuel={fuel_type}, id_municipality={id_municipality}, price={price_threshold} for user: {query.from_user.id}")
        
        # Delete the alert using the data manager's remove_price_alert method
        success = menorca_data_manager.remove_price_alert(
            user_id=query.from_user.id,
            fuel_type=fuel_type,
            id_municipality=id_municipality
        )
        
        if success:
            # Get fuel name for confirmation
            try:
                fuel_name = FUEL_TYPES[fuel_type]['display_name']
            except KeyError:
                fuel_name = fuel_type.replace('_', ' ').title()
            
            # Get municipality name
            if id_municipality:
                municipality_name = get_municipality_display_name(id_municipality)
            else:
                municipality_name = 'Tota Menorca'
            
            await query.answer(f"✅ Alerta eliminada: {fuel_name} - {municipality_name}", show_alert=True)
            logger.info(f"✅ Successfully deleted alert: fuel={fuel_type}, id_municipality={id_municipality} for user: {query.from_user.id}")
            
            # Refresh the removal list
            await remove_user_alerts(update, context)
        else:
            await query.answer("❌ Error eliminant l'alerta", show_alert=True)
            logger.error(f"❌ Failed to delete alert: fuel={fuel_type}, id_municipality={id_municipality} for user: {query.from_user.id}")
            
    except (ValueError, IndexError) as e:
        logger.error(f"❌ Invalid alert deletion callback data: {query.data}, error: {e}")
        await query.answer("❌ Error en les dades de l'alerta", show_alert=True)
    except Exception as e:
        logger.error(f"❌ Unexpected error deleting alert: {e}")
        await query.answer("❌ Error inesperat", show_alert=True)
    
    return NIVELL1

# ===============================
# INFO HANDLER
# ===============================

@error_handler
async def info(update: Update, context: CallbackContext):
    """Show bot information."""
    query = update.callback_query
    await query.answer()
    
    last_update = menorca_data_manager.get_last_update_time()
    info_message = M_INFO.format(last_update)
    
    keyboard = [[InlineKeyboardButton("🏠 Menú Principal", callback_data=str(INICI))]]
    
    await query.edit_message_text(
        info_message,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=False,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return NIVELL1

# ===============================
# INLINE QUERY HANDLER
# ===============================

@error_handler
async def inline_query(update: Update, context: CallbackContext):
    """Handle inline queries."""
    query = update.inline_query.query
    
    if query == "":
        # Default results
        cheapest_stations_df = menorca_data_manager.get_stations_by_fuel_ascending(DEFAULT_FUEL_TYPE, 5)
        expensive_stations_df = menorca_data_manager.get_stations_by_fuel_descending(DEFAULT_FUEL_TYPE, 5)
        
        # Format results
        cheapest_msg = "🏆 *MÉS BARATES*\n\n"
        expensive_msg = "💸 *MÉS CARES*\n\n"
        
        for _, station in cheapest_stations_df.iterrows():
            cheapest_msg += format_station_message(station) + "\n\n"
        
        for _, station in expensive_stations_df.iterrows():
            expensive_msg += format_station_message(station) + "\n\n"
        
        results = [
            InlineQueryResultArticle(
                id=str(uuid4()),
                title="✅ Més Barates",
                input_message_content=InputTextMessageContent(
                    cheapest_msg, 
                    parse_mode=ParseMode.MARKDOWN, 
                    disable_web_page_preview=True
                ),
            ),
            InlineQueryResultArticle(
                id=str(uuid4()),
                title="💸 Més Cares",
                input_message_content=InputTextMessageContent(
                    expensive_msg, 
                    parse_mode=ParseMode.MARKDOWN, 
                    disable_web_page_preview=True
                ),
            ),
        ]

        await update.inline_query.answer(results)

# ===============================
# ADMIN HANDLERS
# ===============================

@error_handler
@admin_required
async def admin_stats(update: Update, context: CallbackContext):
    """Show admin statistics."""
    stats = menorca_data_manager.get_user_stats()
    
    message = M_ADMIN_STATS.format(
        stats['total_users'],
        stats['active_users'],
        stats['today_interactions'],
        stats['active_alerts']
    )
    
    if update.callback_query:
        await update.callback_query.edit_message_text(message, parse_mode=ParseMode.MARKDOWN, reply_markup=create_back_to_main_keyboard())
    else:
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN, reply_markup=create_back_to_main_keyboard())

@error_handler
@admin_required
async def debug_historical_command(update: Update, context: CallbackContext):
    """Debug command to check historical data in database."""
    user = update.message.from_user
    
    debug_msg = "🔍 **Historical Data Debug**\n\n"
    
    # 1. Clean up NULL records first
    try:
        cleaned_count = menorca_data_manager.cleanup_historical_null_records()
        debug_msg += f"✅ Cleaned {cleaned_count} NULL records\n\n"
    except Exception as e:
        logger.error(f"Error cleaning NULL records: {e}")
        debug_msg += f"❌ Error cleaning NULL records: {e}\n\n"
    
    # 2. Run the debug check
    try:
        menorca_data_manager.debug_historical_data(fuel_type='GASOLINA_95_E5', days=7)
        debug_msg += "✅ Debug analysis completed\n\n"
    except Exception as e:
        logger.error(f"Error in debug analysis: {e}")
        debug_msg += f"❌ Error in debug analysis: {e}\n\n"
    
    # 3. Try to manually store today's snapshot if needed
    try:
        menorca_data_manager.store_daily_snapshot()
        debug_msg += "✅ Today's snapshot stored\n\n"
    except Exception as e:
        logger.error(f"Error storing snapshot: {e}")
        debug_msg += f"❌ Error storing snapshot: {e}\n\n"
    
    # 4. Test chart generation
    try:
        chart_buffer = menorca_data_manager.generate_price_chart('GASOLINA_95_E5', 7)
        if chart_buffer:
            debug_msg += "✅ Chart generation: SUCCESS\n"
            debug_msg += "Chart would be generated successfully now!\n\n"
        else:
            debug_msg += "❌ Chart generation: FAILED\n"
            debug_msg += "Still no data for chart generation.\n\n"
    except Exception as e:
        logger.error(f"Error testing chart generation: {e}")
        debug_msg += f"❌ Chart generation error: {e}\n\n"
    
    debug_msg += "📋 **What this command did:**\n"
    debug_msg += "1. Cleaned up NULL records from database\n"
    debug_msg += "2. Analyzed historical data availability\n"
    debug_msg += "3. Attempted to store today's snapshot\n"
    debug_msg += "4. Tested chart generation\n\n"
    debug_msg += "📊 Check your server logs for detailed output.\n\n"
    debug_msg += "If chart generation still fails, the issue is that\n"
    debug_msg += "there isn't enough valid historical data for the\n"
    debug_msg += "requested time period."
    
    await update.message.reply_text(
        debug_msg, 
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=create_back_to_main_keyboard()
    )

@error_handler
async def create_alert_from_municipality(update: Update, context: CallbackContext):
    """Create alert from municipality page - go directly to fuel selection."""
    query = update.callback_query
    await query.answer()
    
    logger.info(f"Alert creation triggered from municipality page. Callback data: {query.data}")
    
    # Parse municipality from callback data: alert_CREATE_07032 -> 07032
    callback_parts = query.data.split('_')
    if len(callback_parts) >= 3 and callback_parts[1] == 'CREATE':
        id_municipality = callback_parts[2]
        logger.info(f"Parsed municipality ID: {id_municipality}")
    else:
        logger.error(f"Invalid callback data for municipality alert: {query.data}")
        await query.edit_message_text("❌ Error en les dades", reply_markup=create_back_to_main_keyboard())
        return NIVELL1
    
    # Validate municipality
    if not validate_municipality(id_municipality):
        logger.error(f"Invalid municipality ID: {id_municipality}")
        await query.edit_message_text("❌ Municipi no vàlid", reply_markup=create_back_to_main_keyboard())
        return NIVELL1
    
    # Store municipality in context for later use
    context.user_data['alert_municipality'] = id_municipality
    logger.info(f"Stored municipality ID {id_municipality} in context")
    
    # Get available fuel types for this municipality
    available_fuel_types = get_available_fuel_types_for_municipality(id_municipality)
    
    if not available_fuel_types:
        # Use display name for user-facing text
        municipality_display_name = get_municipality_display_name(id_municipality)
            
        await query.edit_message_text(
            f"❌ No hi ha combustibles disponibles a {municipality_display_name}",
            reply_markup=create_back_to_main_keyboard()
        )
        return NIVELL1
    
    # Show fuel selection menu - only for available fuel types
    keyboard = []
    for fuel_key in available_fuel_types:
        if fuel_key in FUEL_TYPES:
            fuel_data = FUEL_TYPES[fuel_key]
            button_text = f"{fuel_data['emoji']} {fuel_data['display_name']}"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"{ALERT_PREFIX}FUEL_FROM_MUNI_{fuel_key}")])
    
    keyboard.append([InlineKeyboardButton("🏠 Menú Principal", callback_data=str(INICI))])  # Back to main menu
    
    # Use display name for user-facing text
    municipality_display_name = get_municipality_display_name(id_municipality)
    
    logger.info(f"Showing {len(available_fuel_types)} available fuel types for municipality: {municipality_display_name}")
    
    fuel_count_text = f"({len(available_fuel_types)} combustibles disponibles)"
    await query.edit_message_text(
        f"🔔 *Crear alerta per {municipality_display_name}*\n\n{M_ALERT_FUEL_SELECT}\n\n💡 *Només es mostren els combustibles disponibles a {municipality_display_name} {fuel_count_text}*",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ALERT_FUEL_SELECT

@error_handler
async def create_alert_municipality_fuel_selected(update: Update, context: CallbackContext):
    """Handle fuel selection from municipality alert creation."""
    query = update.callback_query
    await query.answer()
    
    logger.info(f"Fuel selection from municipality alert. Callback data: {query.data}")
    
    # Parse fuel type from callback data: alert_FUEL_FROM_MUNI_GASOLEO_A -> GASOLEO_A
    callback_parts = query.data.split('_')
    if len(callback_parts) >= 5 and callback_parts[1] == 'FUEL' and callback_parts[2] == 'FROM' and callback_parts[3] == 'MUNI':
        fuel_type = '_'.join(callback_parts[4:])  # Handle fuel types with underscores
        logger.info(f"Parsed fuel type: {fuel_type}")
    else:
        logger.error(f"Invalid callback data for fuel selection: {query.data}")
        await query.edit_message_text("❌ Error en les dades", reply_markup=create_back_to_main_keyboard())
        return NIVELL1
    
    # Validate fuel type
    if not validate_fuel_type(fuel_type):
        logger.error(f"Invalid fuel type: {fuel_type}")
        await query.edit_message_text("❌ Tipus de combustible no vàlid", reply_markup=create_back_to_main_keyboard())
        return NIVELL1
    
    # Get municipality from context
    id_municipality = context.user_data.get('alert_municipality')
    logger.info(f"Retrieved municipality ID from context: {id_municipality}")
    
    if not validate_municipality(id_municipality):
        logger.error(f"No valid municipality ID in context: {id_municipality}")
        await query.edit_message_text("❌ Error: municipi no trobat", reply_markup=create_back_to_main_keyboard())
        return NIVELL1
    
    # Additional validation: check if the fuel type is actually available in this municipality
    available_fuel_types = get_available_fuel_types_for_municipality(id_municipality)
    if fuel_type not in available_fuel_types:
        logger.error(f"Fuel type {fuel_type} not available in municipality {id_municipality}")
        # Use display name for user-facing text
        municipality_display_name = get_municipality_display_name(id_municipality)
        
        fuel_display_name = FUEL_TYPES.get(fuel_type, {}).get('display_name', fuel_type)
        await query.edit_message_text(
            f"❌ {fuel_display_name} no està disponible a {municipality_display_name}",
            reply_markup=create_back_to_main_keyboard()
        )
        return NIVELL1
    
    # Store fuel type in context
    context.user_data['alert_fuel'] = fuel_type
    logger.info(f"Stored fuel type {fuel_type} in context")
    
    # Show price input
    fuel_name = FUEL_TYPES[fuel_type]['display_name']
    # Use display name for user-facing text
    municipality_display_name = get_municipality_display_name(id_municipality)
    
    logger.info(f"Showing price input for {fuel_name} in {municipality_display_name}")
    
    await query.edit_message_text(
        f"🔔 *Alerta per {fuel_name} a {municipality_display_name}*\n\n{M_ALERT_PRICE_INPUT}",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=create_back_to_main_keyboard()
    )
    
    return ALERT_PRICE_INPUT

# ===============================
# CONVERSATION HANDLER SETUP
# ===============================

def get_conversation_handler():
    """Create and return the main conversation handler following technical description pattern."""
    
    conv_handler = ConversationHandler(
        name="menorca_fuel_bot",  # Add name for persistence
        entry_points=[CommandHandler('start', start)],
        states={
            NIVELL1: [
                CallbackQueryHandler(price_menu, pattern=f'^{PREU}$'),
                CallbackQueryHandler(fuel_type_menu, pattern=f'^{COMBUSTIBLE}$'),
                CallbackQueryHandler(municipality_menu, pattern=f'^{POBLE}$'),
                CallbackQueryHandler(info, pattern=f'^{INFO}$'),
                CallbackQueryHandler(price_charts_menu, pattern=f'^{CHARTS}$'),
                CallbackQueryHandler(location_search, pattern=f'^{LOCATION}$'),
                CallbackQueryHandler(price_alerts_menu, pattern=f'^{ALERTS}$'),
                CallbackQueryHandler(create_alert_from_municipality, pattern=f'^{ALERT_PREFIX}CREATE_'),
                CallbackQueryHandler(delete_specific_alert, pattern=f'^{ALERT_DELETE}_'),
                CallbackQueryHandler(start_over, pattern=f'^{INICI}$'),
            ],
            NIVELL2: [
                # Price handlers
                CallbackQueryHandler(cheapest_stations, pattern=f'^{BARATES}$'),
                CallbackQueryHandler(most_expensive_stations, pattern=f'^{CARES}$'),
                
                # Fuel type handlers
                CallbackQueryHandler(fuel_type_info, pattern=f'^{FUEL_PREFIX}'),
                
                # Municipality handlers  
                CallbackQueryHandler(municipality_menu, pattern=r'^page_\d+$'),
                CallbackQueryHandler(municipality_info, pattern=f'^{TOWN_PREFIX}'),
                
                # Chart handlers
                CallbackQueryHandler(chart_period_selection, pattern=f'^{CHART_FUEL_PREFIX}'),
                CallbackQueryHandler(generate_chart, pattern=f'^{CHART_PREFIX}'),
                
                # Alert handlers
                CallbackQueryHandler(create_alert_fuel_selection, pattern=f'^{ALERT_CREATE}$'),
                CallbackQueryHandler(list_user_alerts, pattern=f'^{ALERT_LIST}$'),
                CallbackQueryHandler(remove_user_alerts, pattern=f'^{ALERT_REMOVE}$'),
                CallbackQueryHandler(delete_specific_alert, pattern=f'^{ALERT_DELETE}_'),
                
                # Location handler
                MessageHandler(filters.LOCATION, handle_location),
                
                # Back handlers
                CallbackQueryHandler(start_over, pattern=f'^{INICI}$'),
                CallbackQueryHandler(price_menu, pattern=f'^{PREU}$'),
                CallbackQueryHandler(fuel_type_menu, pattern=f'^{COMBUSTIBLE}$'),
                CallbackQueryHandler(municipality_menu, pattern=f'^{POBLE}$'),
                CallbackQueryHandler(price_charts_menu, pattern=f'^{CHARTS}$'),
            ],
            ALERT_FUEL_SELECT: [
                CallbackQueryHandler(create_alert_municipality_fuel_selected, pattern=f'^{ALERT_PREFIX}FUEL_FROM_MUNI_'),  # More specific pattern first
                CallbackQueryHandler(create_alert_municipality_selection, pattern=f'^{ALERT_PREFIX}FUEL_'),  # General pattern second
                CallbackQueryHandler(price_alerts_menu, pattern=f'^{ALERTS}$'),
                CallbackQueryHandler(start_over, pattern=f'^{INICI}$'),  # Handle "Menú Principal" button
            ],
            ALERT_MUNICIPALITY_SELECT: [
                CallbackQueryHandler(create_alert_price_input, pattern=f'^{ALERT_PREFIX}MUNICIPALITY_'),
                CallbackQueryHandler(price_alerts_menu, pattern=f'^{ALERTS}$'),
                CallbackQueryHandler(start_over, pattern=f'^{INICI}$'),  # Handle "Menú Principal" button
            ],
            ALERT_PRICE_INPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_alert_price),
                CallbackQueryHandler(start_over, pattern=f'^{INICI}$'),  # Handle "Menú Principal" button
            ],
        },
        fallbacks=[
            CommandHandler('start', start),
            CallbackQueryHandler(start_over, pattern=f'^{INICI}$'),  # Handle "Menú Principal" button
            MessageHandler(filters.Regex('^🔙'), start_over),
            MessageHandler(filters.Regex('Menú principal'), start_over),
            MessageHandler(filters.Regex('Tornar al menú'), start_over),
            MessageHandler(filters.TEXT & filters.Regex('menú|menu|main|principal|inicio|inici'), start_over),
        ],
        persistent=True,  # Enable persistence
        allow_reentry=True,
    )
    
    return conv_handler

# ===============================
# SCHEDULED TASK FOR ALERTS
# ===============================

async def check_and_send_alerts(context: CallbackContext):
    """Scheduled task to check and send price alerts."""
    try:
        alerts = menorca_data_manager.check_price_alerts()
        
        for alert in alerts:
            # Handle unknown fuel types gracefully
            try:
                fuel_name = FUEL_TYPES[alert['fuel_type']]['display_name']
            except KeyError:
                # Fallback for unknown fuel types
                fuel_name = alert['fuel_type'].replace('_', ' ').title()
                logger.warning(f"Unknown fuel type in alert notification: {alert['fuel_type']}")
            
            municipality_display_name = get_municipality_display_name(alert.get('id_municipality'))

            message = M_ALERT_TRIGGERED.format(
                fuel_name,
                alert['station_name'],
                alert['current_price'],
                municipality_display_name,
                format_station_message(alert['station_details'])
            )
            
            try:
                await context.bot.send_message(
                    chat_id=alert['user_id'],
                    text=message,
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=True,
                    reply_markup=create_back_to_main_keyboard()
                )
                logger.info(f"Sent alert to user {alert['user_id']}")
            except Exception as e:
                logger.error(f"Error sending alert to user {alert['user_id']}: {e}")
        
        if alerts:
            logger.info(f"Processed {len(alerts)} price alerts")
            
    except Exception as e:
        logger.error(f"Error in scheduled alert check: {e}")

# ===============================
# MAIN APPLICATION
# ===============================

def main():
    """Main application entry point following technical description pattern."""
    try:
        # Initialize data manager
        menorca_data_manager.connect()
        menorca_data_manager.load_data_from_db()
        print("✅ Menorca data manager initialized successfully")
        
        # Create persistence with explicit path and error handling
        persistence_file = "menorca_bot_persistence.pkl"
        try:
            # Create persistence directory if it doesn't exist
            os.makedirs("data", exist_ok=True)
            persistence_file = os.path.join("data", "menorca_bot_persistence.pkl")
            
            persistence = PicklePersistence(filepath=persistence_file)
            print(f"📁 Persistence file: {os.path.abspath(persistence_file)}")
        except Exception as e:
            print(f"⚠️ Could not create persistence: {e}")
            print("Running without persistence...")
            persistence = None
        
        # Create application
        if persistence:
            application = Application.builder().token(secret.secret['bot_token']).persistence(persistence).build()
            print("✅ Bot created with conversation persistence enabled")
        else:
            application = Application.builder().token(secret.secret['bot_token']).build()
            print("⚠️ Bot created WITHOUT conversation persistence")
        
        # Add conversation handler
        application.add_handler(get_conversation_handler())
        
        # Add global fallback for "Menú Principal" button (INICI callback)
        application.add_handler(CallbackQueryHandler(start_over, pattern=f'^{INICI}$'))
        
        # Add inline query handler
        application.add_handler(InlineQueryHandler(inline_query))
        
        # Add admin commands
        application.add_handler(CommandHandler('stats', admin_stats))
        application.add_handler(CommandHandler('debug_historical', debug_historical_command))
        application.add_handler(CommandHandler('debug_municipality', debug_municipality_command))
        application.add_handler(CommandHandler('debug_datamanager', debug_datamanager_command))
        application.add_handler(CommandHandler('debug_investigation', debug_investigation_command))
        
        # Add debug commands
        application.add_handler(CommandHandler('status', status_command))
        application.add_handler(CommandHandler('id', get_id_command))
        
        # Schedule alerts check (every 10 minutes)
        job_queue = application.job_queue
        job_queue.run_repeating(check_and_send_alerts, interval=600, first=10)
        
        # Add error handler
        async def error_callback(update: Update, context: CallbackContext):
            logger.error(f"Exception while handling an update: {context.error}", exc_info=context.error)
        
        application.add_error_handler(error_callback)
        
        logger.info("Starting Menorca Fuel Prices Bot...")
        
        # Run the bot
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        sys.exit(1)

# ===============================
# DEBUG COMMANDS
# ===============================

@error_handler
async def status_command(update: Update, context: CallbackContext):
    """Debug command to check persistence status."""
    user = update.message.from_user
    user_data = context.user_data
    
    status_msg = f"🔍 **Status Debug for {user.first_name}**\n\n"
    status_msg += f"User ID: `{user.id}`\n"
    status_msg += f"User data keys: `{list(user_data.keys()) if user_data else 'None'}`\n"
    status_msg += f"Municipality page: `{user_data.get('municipality_page', 'Not set')}`\n"
    status_msg += f"Current municipality: `{user_data.get('current_municipality', 'Not set')}`\n"
    status_msg += f"Alert fuel: `{user_data.get('alert_fuel', 'Not set')}`\n"
    status_msg += f"Alert municipality: `{user_data.get('alert_municipality', 'Not set')}`\n"
    
    # Test persistence by setting a test value
    import time
    test_time = int(time.time())
    user_data['last_status_check'] = test_time
    user_data['test_persistence'] = f"Test_{test_time}"
    status_msg += f"\n✅ Set test value: `{test_time}`\n"
    status_msg += "Restart the bot and run /status again to verify persistence."
    
    await update.message.reply_text(
        status_msg, 
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=create_back_to_main_keyboard()
    )

@error_handler
async def get_id_command(update: Update, context: CallbackContext):
    """Simple command to get user's Telegram ID for admin setup."""
    user = update.message.from_user
    
    def escape_markdown(text):
        if not text:
            return "Unknown"
        # Escape markdown special characters
        return text.replace('_', '\\_').replace('*', '\\*').replace('[', '\\[').replace('`', '\\`')
    
    id_msg = f"🆔 **Your Telegram Information**\n\n"
    id_msg += f"**User ID:** `{user.id}`\n"
    id_msg += f"**First Name:** {escape_markdown(user.first_name)}\n"
    if user.last_name:
        id_msg += f"**Last Name:** {escape_markdown(user.last_name)}\n"
    if user.username:
        id_msg += f"**Username:** @{escape_markdown(user.username)}\n"
    id_msg += f"**Language:** {user.language_code or 'Unknown'}\n\n"
    
    id_msg += f"💡 **For Admin Setup:**\n"
    id_msg += f"Copy this User ID: `{user.id}`\n"
    
    await update.message.reply_text(
        id_msg, 
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=create_back_to_main_keyboard()
    )

@error_handler
@admin_required
async def debug_municipality_command(update: Update, context: CallbackContext):
    """Debug command to test municipality mappings."""
    # Handle both callback queries and text messages
    if update.callback_query:
        user = update.callback_query.from_user
    else:
        user = update.message.from_user
    
    debug_msg = "🔍 **Municipality Mapping Debug**\n\n"
    
    # Test each municipality mapping
    for id_municipality, muni_data in MUNICIPALITIES.items():
        debug_msg += f"🔸 **{get_municipality_display_name(id_municipality)}**\n"
        debug_msg += f"  ID: `{id_municipality}`\n"
        
        try:
            available_fuels = get_available_fuel_types_for_municipality(id_municipality)
            debug_msg += f"  Available fuels: {len(available_fuels)}\n"
            if available_fuels:
                fuel_names = [FUEL_TYPES[f]['display_name'] for f in available_fuels if f in FUEL_TYPES]
                debug_msg += f"  Types: {', '.join(fuel_names)}\n"
            else:
                debug_msg += f"  ❌ No fuels found\n"
        except Exception as e:
            debug_msg += f"  ❌ Error: {e}\n"
        
        debug_msg += "\n"
    
    # Also run the debug function to log details
    debug_municipality_mapping()
    
    debug_msg += "📋 **Summary completed**\n"
    debug_msg += "Check server logs for detailed output."
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            debug_msg, 
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=create_back_to_main_keyboard()
        )
    else:
        await update.message.reply_text(
            debug_msg, 
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=create_back_to_main_keyboard()
        )

def test_data_manager_municipality_query():
    """Test function to verify data manager municipality queries work correctly."""
    logger.info("=== Testing Data Manager Municipality Queries ===")
    
    # Test each municipality
    for id_municipality, muni_data in MUNICIPALITIES.items():
        logger.info(f"\nTesting municipality: '{muni_data['display_name']}' (ID: {id_municipality})")
        try:
            # Query the data manager directly
            stations_df = menorca_data_manager.get_stations_by_municipality(id_municipality)
            logger.info(f"  Result shape: {stations_df.shape if not stations_df.empty else 'EMPTY'}")
            
            if not stations_df.empty:
                # Show station details
                for idx, station in stations_df.iterrows():
                    rotulo = station.get('Rotulo', 'Unknown')
                    localidad = station.get('Localidad', 'Unknown')
                    logger.info(f"    Station: {rotulo} (Localidad: {localidad})")
                    
                    # Show fuel prices
                    for fuel_key in ['GASOLINA_95_E5', 'GASOLEO_A']:
                        if fuel_key == 'GASOLINA_95_E5':
                            col = 'Precio_Gasolina_95_E5'
                        else:
                            col = 'Precio_Gasoleo_A'
                        
                        if col in station:
                            price = station[col]
                            logger.info(f"      {col}: {price}")
            else:
                logger.warning(f"  No stations found for municipality ID: '{id_municipality}'")
                
        except Exception as e:
            logger.error(f"  Error querying municipality ID '{id_municipality}': {e}", exc_info=True)
    
    logger.info("=== End Data Manager Test ===")

@error_handler
@admin_required
async def debug_datamanager_command(update: Update, context: CallbackContext):
    """Debug command to test data manager directly."""
    # Handle both callback queries and text messages
    if update.callback_query:
        user = update.callback_query.from_user
    else:
        user = update.message.from_user
    
    debug_msg = "🔍 **Data Manager Test**\n\n"
    debug_msg += "Testing data manager municipality queries...\n\n"
    
    # Run the test function
    test_data_manager_municipality_query()
    
    debug_msg += "✅ Test completed!\n"
    debug_msg += "Check server logs for detailed output."
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            debug_msg, 
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=create_back_to_main_keyboard()
        )
    else:
        await update.message.reply_text(
            debug_msg, 
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=create_back_to_main_keyboard()
        )

def investigate_data_manager_data():
    """Investigate what municipality data the data manager actually has."""
    logger.info("=== Investigating Data Manager Raw Data ===")
    
    try:
        # Get all stations data directly from the data manager
        all_stations = menorca_data_manager.get_all_stations()  # This might not exist, let's try alternatives
        
        if hasattr(all_stations, 'empty') and not all_stations.empty:
            # Get unique municipality names from the data
            unique_localities = all_stations['Localidad'].unique() if 'Localidad' in all_stations.columns else []
            logger.info(f"Unique Localidad values in data manager: {list(unique_localities)}")
            
            # Compare with our expected values
            for key, expected_name in MUNICIPALITIES.items():
                logger.info(f"Looking for '{expected_name}' (key: {key})")
                if expected_name in unique_localities:
                    count = len(all_stations[all_stations['Localidad'] == expected_name])
                    logger.info(f"  ✅ Found {count} stations with Localidad='{expected_name}'")
                else:
                    logger.warning(f"  ❌ '{expected_name}' not found in data manager")
                    # Check for similar names
                    similar = [loc for loc in unique_localities if expected_name.lower() in loc.lower() or loc.lower() in expected_name.lower()]
                    if similar:
                        logger.info(f"    Similar names found: {similar}")
            
    except Exception as e:
        logger.error(f"Error investigating data manager data: {e}")
        
        # Try alternative approach - test with sample queries
        logger.info("Trying alternative approach - testing sample municipalities:")
        test_municipalities = ["MAO", "CIUTADELLA DE MENORCA", "ALAIOR", "SANT LLUIS"]
        
        for muni in test_municipalities:
            try:
                result = menorca_data_manager.get_stations_by_municipality(muni)
                if not result.empty:
                    logger.info(f"  ✅ '{muni}': Found {len(result)} stations")
                    logger.info(f"    First station Localidad: '{result.iloc[0]['Localidad']}'")
                else:
                    logger.warning(f"  ❌ '{muni}': No stations found")
            except Exception as e2:
                logger.error(f"  ❌ '{muni}': Error - {e2}")
    
    logger.info("=== End Data Manager Investigation ===")

@error_handler
@admin_required
async def debug_investigation_command(update: Update, context: CallbackContext):
    """Debug command to investigate data manager data."""
    # Handle both callback queries and text messages
    if update.callback_query:
        user = update.callback_query.from_user
    else:
        user = update.message.from_user
    
    debug_msg = "🔍 **Data Manager Investigation**\n\n"
    debug_msg += "Investigating what municipality data exists...\n\n"
    
    # Run the investigation function
    investigate_data_manager_data()
    
    debug_msg += "✅ Investigation completed!\n"
    debug_msg += "Check server logs for detailed analysis of municipality names."
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            debug_msg, 
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=create_back_to_main_keyboard()
        )
    else:
        await update.message.reply_text(
            debug_msg, 
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=create_back_to_main_keyboard()
        )

if __name__ == '__main__':
    main()