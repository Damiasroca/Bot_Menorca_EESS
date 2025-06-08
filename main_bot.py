import os
from telegram.ext import Application, CommandHandler, ConversationHandler, CallbackQueryHandler, CallbackContext, PicklePersistence, InlineQueryHandler, MessageHandler, filters
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update, InlineQueryResultArticle, InputTextMessageContent, KeyboardButton, ReplyKeyboardMarkup
from telegram.constants import ParseMode
from data_manager import data_manager
import logging
import sys
import secret
from uuid import uuid4
from constants import *
import datetime
from functools import wraps

# Setup logging to file and console
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Console handler
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(log_formatter)
logger.addHandler(stream_handler)

# File handler
try:
    log_file_path = "/home/damia/Bot_Menorca_EESS/logs/main_bot.log"
    # Ensure directory exists
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)
    logger.info(f"Logging to {log_file_path}")
except (OSError, IOError) as e:
    logger.warning(f"Could not set up file logging to {log_file_path}: {e}")

def error_handler(func):
    @wraps(func)
    async def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        try:
            # Track user interaction
            track_user_from_update(update)
            
            return await func(update, context, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in handler {func.__name__}: {e}", exc_info=True)
            if query := update.callback_query:
                await query.answer(text="An error occurred.", show_alert=True)
            elif update.message:
                await update.message.reply_text("An error occurred. Please try again.")
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
            data_manager.track_user_interaction(
                user_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                language_code=user.language_code
            )
    except Exception as e:
        logger.error(f"Error tracking user interaction: {e}")

def format_station_message(est, loc, *args):
    """Formats the message for a single station."""
    base_message = f"🔸*{est.Rotulo}*\n[{est.Direccion}]({loc})"
    if 'Benzina 95 E5' in args:
        base_message += f"\nBenzina 95 E5 *{est.Precio_Gasolina_95_E5}*€"
    if 'Diesel A' in args:
        base_message += f"\nDiesel A *{est.Precio_Gasoleo_A}*€"
    if 'Gasoli A' in args:
        base_message += f"\nGasoli A *{est.Precio_Gasoleo_A}*€"
    if 'Gasoli B' in args:
        base_message += f"\nGasoli B *{est.Precio_Gasoleo_B}*€"
    if 'Gasoli Premium' in args:
        base_message += f"\nGasoli Premium *{est.Precio_Gasoleo_Premium}*€"
    if 'GLP' in args:
        base_message += f"\nGLP *{est.Precio_Gases_Licuados_del_petroleo}*€"
    return base_message

def format_location(lat, long):
    return f'https://www.google.com/maps/@{lat.replace(",", ".")},{long.replace(",", ".")},20z'

@error_handler
async def start(update: Update, context: CallbackContext):
    user = update.message.from_user
    await update.message.reply_text(f"Benvingut *{user.username.upper()}*.\nMés ⛽️ per menys 💶!\n"
                                    "Preus actualitzats cada 10 minuts.", parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

    button1 = InlineKeyboardButton(B1, callback_data=str(PREU))
    button2 = InlineKeyboardButton(B2, callback_data=str(COMBUSTIBLE))
    button3 = InlineKeyboardButton(B3, callback_data=str(POBLE))
    button4 = InlineKeyboardButton(B4, callback_data=str(INFO))
    button21 = InlineKeyboardButton(B21, callback_data=str(CHARTS))
    button22 = InlineKeyboardButton(B22, callback_data=str(LOCATION))
    button23 = InlineKeyboardButton(B23, callback_data=str(ALERTS))

    await update.message.reply_text(
        text=M_INSTRUCT, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([
            [button1, button2],
            [button3, button4],
            [button21, button22],
            [button23]
        ])
    )
    return NIVELL1

@error_handler
async def start_over(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    button1 = InlineKeyboardButton(B1, callback_data=str(PREU))
    button2 = InlineKeyboardButton(B2, callback_data=str(COMBUSTIBLE))
    button3 = InlineKeyboardButton(B3, callback_data=str(POBLE))
    button4 = InlineKeyboardButton(B4, callback_data=str(INFO))
    button21 = InlineKeyboardButton(B21, callback_data=str(CHARTS))
    button22 = InlineKeyboardButton(B22, callback_data=str(LOCATION))
    button23 = InlineKeyboardButton(B23, callback_data=str(ALERTS))

    await query.edit_message_text(
        text=M_INSTRUCT, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([
            [button1, button2],
            [button3, button4],
            [button21, button22],
            [button23]
        ])
    )
    return NIVELL1

@error_handler
async def preu(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    button5 = InlineKeyboardButton(
        B5, callback_data=str(INICI)
    )
    button6 = InlineKeyboardButton(
        B6, callback_data=str(BARATES)
    )
    button7 = InlineKeyboardButton(
        B7, callback_data=str(CARES)
    )
    missatge_preu = '*SELECCIONA :*'
    await query.edit_message_text(
        text=missatge_preu, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([
            [button6, button7],
            [button5]
        ])
    )
    return NIVELL2

@error_handler
async def mes_barates(update, context=CallbackContext):
    output_barates_df = data_manager.estacions_servei_extraccio_benzina_ascendent()
    output_barates = output_barates_df.head(5)

    query = update.callback_query
    await query.answer()
    
    button5 = InlineKeyboardButton(B5, callback_data=str(PREU))

    messages = []
    for est in output_barates.itertuples(index=False):
        loc = format_location(est.Latitud, est.Longitud_WGS84)
        messages.append(format_station_message(est, loc, 'Benzina 95 E5', 'Diesel A'))
    
    missatge_preu = "\n\n".join(messages)

    await query.edit_message_text(
        text=missatge_preu, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([[button5]])
    )

    return NIVELL1


@error_handler
async def mes_barates_inlinequery(update: Update, context=CallbackContext):
    output_barates_df = data_manager.estacions_servei_extraccio_benzina_ascendent().head(5)
    
    missatge_preu = "**MÉS BARATES**\n\n"
    messages = []
    for est in output_barates_df.itertuples(index=False):
        loc = format_location(est.Latitud, est.Longitud_WGS84)
        messages.append(
            f"🔸*{est.Rotulo}*\n[{est.Direccion}]({loc})\n{est.Localidad}\nBenzina 95 E5 = *{est.Precio_Gasolina_95_E5}*€\nDiesel A = *{est.Precio_Gasoleo_A}*€."
        )
    missatge_preu += "\n\n".join(messages)
    
    return missatge_preu
    
@error_handler
async def mes_cares(update: Update, context=CallbackContext):
    output_cares_df = data_manager.estacions_servei_extraccio_benzina_descendent().head(5)

    query = update.callback_query
    await query.answer()
    
    button5 = InlineKeyboardButton(B5, callback_data=str(PREU))

    messages = []
    for est in output_cares_df.itertuples(index=False):
        loc = format_location(est.Latitud, est.Longitud_WGS84)
        messages.append(format_station_message(est, loc, 'Benzina 95 E5', 'Diesel A'))

    missatge_preu = "\n\n".join(messages)

    await query.edit_message_text(
        text=missatge_preu, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([[button5]])
    )

    return NIVELL1

@error_handler
async def mes_cares_inlinequery(update: Update, context=CallbackContext):
    output_cares_df = data_manager.estacions_servei_extraccio_benzina_descendent().head(5)

    missatge_preu = "*MÉS CARES*\n\n"
    messages = []
    for est in output_cares_df.itertuples(index=False):
        loc = format_location(est.Latitud, est.Longitud_WGS84)
        messages.append(
            f"🔸*{est.Rotulo}*\n[{est.Direccion}]({loc})\n{est.Localidad}\nBenzina 95 E5 = *{est.Precio_Gasolina_95_E5}*€\nDiesel A = *{est.Precio_Gasoleo_A}*€."
        )
    missatge_preu += "\n\n".join(messages)

    return missatge_preu

@error_handler
async def tipus_combustible(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    button5 = InlineKeyboardButton(
        B5, callback_data=str(INICI)
    )
    button8 = InlineKeyboardButton(
        B8, callback_data=str(BENZINA)
    )
    button9 = InlineKeyboardButton(
        B9, callback_data=str(GASOLIA)
    )
    button10 = InlineKeyboardButton(
        B10, callback_data=str(GASOLIB)
    )
    button11 = InlineKeyboardButton(
        B11, callback_data=str(GASOLIP)
    )
    button12 = InlineKeyboardButton(
        B12, callback_data=str(GLP)
    )
    missatge_preu = '*SELECCIONA :*'
    await query.edit_message_text(
        text=missatge_preu, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([
            [button8, button9],
            [button10, button11],
            [button12, button5]
        ])
    )
    return NIVELL2

@error_handler
async def per_municipi(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    button5 = InlineKeyboardButton(
        B5, callback_data=str(INICI)
    )
    button13 = InlineKeyboardButton(
        B13, callback_data=str(P1)
    )
    button14 = InlineKeyboardButton(
        B14, callback_data=str(P2)
    )
    button15 = InlineKeyboardButton(
        B15, callback_data=str(P3)
    )
    button16 = InlineKeyboardButton(
        B16, callback_data=str(P4)
    )
    button17 = InlineKeyboardButton(
        B17, callback_data=str(P5)
    )
    button18 = InlineKeyboardButton(
        B18, callback_data=str(P6)
    )
    button19 = InlineKeyboardButton(
        B19, callback_data=str(P7)
    )
    await query.edit_message_text(
        text=M_INSTRUCT, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([
            [button13, button14, button15],
            [button16, button17, button18],
            [button19, button5]
        ])
    )
    return NIVELL2

@error_handler
async def town_info(update: Update, context: CallbackContext):
    """Generic handler for town information."""
    query = update.callback_query
    await query.answer()

    town = query.data.split('_')[1]
    
    output_df = data_manager.get_town_data(town)

    if output_df.empty:
        missatge = "😨❌No disponible en aquests moments"
    else:
        messages = []
        for est in output_df.itertuples(index=False):
            loc = format_location(est.Latitud, est.Longitud_WGS84)
            messages.append(format_station_message(est, loc, 'Benzina 95 E5', 'Diesel A'))
        missatge = "\n\n".join(messages)

    button5 = InlineKeyboardButton(B5, callback_data=str(POBLE))
    await query.edit_message_text(
        text=missatge,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([[button5]])
    )
    return NIVELL1

@error_handler
async def info(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    button5 = InlineKeyboardButton(
        B5, callback_data=str(INICI)
    )
    missatge_info = "Dades extretes de *Ministerio de Industria, Comercio y Turismo*.\n"\
                    "S'ha comprobat que algunes dades d'ubicació están malament o no son prou precises.\n"\
                    "Ses dades errónees han estat notificades.\n\n"\
                    "*Última actualització de preus:* {}\n\n"\
                    "Escrit per Damia Sintes.\nCodi a [GitHub](https://github.com/Damiasroca/Bot_Menorca_EESS)".format(data_manager.get_last_update_time())
    await query.edit_message_text(
            text = missatge_info, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview= False,
            reply_markup = InlineKeyboardMarkup([
                [button5]
            ])
        )
    return NIVELL1

@error_handler
async def inlinequery(update: Update, context: CallbackContext):
    query = update.inline_query.query

    if query == "":
        mes_barates_result = await mes_barates_inlinequery(update, context)
        mes_cares_result = await mes_cares_inlinequery(update, context)

        results = [
            InlineQueryResultArticle(
                id=str(uuid4()),
                title="✅ Més Barates",
                input_message_content=InputTextMessageContent(mes_barates_result, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True),
            ),
            InlineQueryResultArticle(
                id=str(uuid4()),
                title="🚫 Més Cares",
                input_message_content=InputTextMessageContent(mes_cares_result, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True),
            ),
        ]

        await update.inline_query.answer(results)

@error_handler
async def fuel_info(update: Update, context: CallbackContext):
    """Generic handler for fuel information."""
    query = update.callback_query
    await query.answer()

    fuel_type = query.data.split('_')[1]

    fuel_extractors = {
        'BENZINA': (data_manager.estacions_servei_extraccio_benzina_ascendent, 'Benzina 95 E5'),
        'GASOLIA': (data_manager.carburants_extraccio_diesel_A_ascendent, 'Gasoli A'),
        'GASOLIB': (data_manager.carburants_extraccio_diesel_B_ascendent, 'Gasoli B'),
        'GASOLIP': (data_manager.carburants_extraccio_diesel_premium_ascendent, 'Gasoli Premium'),
        'GLP': (data_manager.carburants_extraccio_GLP_ascendent, 'GLP'),
    }

    if fuel_type in fuel_extractors:
        extractor_func, fuel_name = fuel_extractors[fuel_type]
        output_df = extractor_func()
    else:
        await query.edit_message_text(text="Combustible no trobat.")
        return NIVELL1

    if output_df.empty:
        missatge = "😨❌No disponible en aquests moments"
    else:
        messages = []
        for est in output_df.itertuples(index=False):
            loc = format_location(est.Latitud, est.Longitud_WGS84)
            messages.append(format_station_message(est, loc, fuel_name))

        missatge = "\n\n".join(messages)

    button5 = InlineKeyboardButton(B5, callback_data=str(COMBUSTIBLE))
    await query.edit_message_text(
        text=missatge,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([[button5]])
    )
    return NIVELL1

@error_handler
async def price_charts(update: Update, context: CallbackContext):
    """Handler for price charts feature."""
    query = update.callback_query
    await query.answer()

    button5 = InlineKeyboardButton(B5, callback_data=str(INICI))
    
    # Store fuel type in user data for chart generation
    if query.data.startswith(CHART_FUEL_PREFIX):
        fuel_type = query.data.split('_')[1]
        context.user_data['chart_fuel'] = fuel_type
        
        button24 = InlineKeyboardButton(B24, callback_data=f"{CHART_PREFIX}{fuel_type}_7")
        button25 = InlineKeyboardButton(B25, callback_data=f"{CHART_PREFIX}{fuel_type}_30")
        
        await query.edit_message_text(
            text=f"📊 *{fuel_type} - Selecciona període:*",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [button24, button25],
                [button5]
            ])
        )
        return NIVELL2
    
    await query.edit_message_text(
        text=M_CHART_SELECT, parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(B8, callback_data=f"{CHART_FUEL_PREFIX}BENZINA")],
            [InlineKeyboardButton(B9, callback_data=f"{CHART_FUEL_PREFIX}GASOLIA")],
            [InlineKeyboardButton(B10, callback_data=f"{CHART_FUEL_PREFIX}GASOLIB")],
            [InlineKeyboardButton(B11, callback_data=f"{CHART_FUEL_PREFIX}GASOLIP")],
            [InlineKeyboardButton(B12, callback_data=f"{CHART_FUEL_PREFIX}GLP")],
            [button5]
        ])
    )
    return NIVELL2

@error_handler
async def generate_chart(update: Update, context: CallbackContext):
    """Generate and send a price chart."""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text("📊 Generant gràfic... Espera un moment.")
    
    # Parse callback data
    parts = query.data.split('_')
    fuel_type = parts[1]
    days = int(parts[2])
    
    # Generate chart
    chart_buffer = data_manager.generate_price_chart(fuel_type, days)
    
    if chart_buffer:
        chart_buffer.seek(0)
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo=chart_buffer,
            caption=f"📊 Evolució preus {fuel_type} - Últims {days} dies"
        )
        
        # Return to charts menu
        button5 = InlineKeyboardButton(B5, callback_data=str(CHARTS))
        await query.edit_message_text(
            "Gràfic generat! 📊",
            reply_markup=InlineKeyboardMarkup([[button5]])
        )
    else:
        await query.edit_message_text(
            "❌ No hi ha prou dades històriques per generar el gràfic.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(B5, callback_data=str(CHARTS))
            ]])
        )
    
    return NIVELL1

@error_handler
async def location_search(update: Update, context: CallbackContext):
    """Handler for location-based search."""
    query = update.callback_query
    await query.answer()

    # Create location request keyboard
    location_keyboard = ReplyKeyboardMarkup([
        [KeyboardButton("📍 Compartir ubicació", request_location=True)]
    ], one_time_keyboard=True, resize_keyboard=True)

    await query.edit_message_text(M_LOCATION_REQUEST, parse_mode=ParseMode.MARKDOWN)
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text="Toca el botó per compartir la teva ubicació:",
        reply_markup=location_keyboard
    )
    
    return NIVELL2

@error_handler
async def handle_location(update: Update, context: CallbackContext):
    """Handle received location and find nearby stations."""
    if update.message.location:
        user_lat = update.message.location.latitude
        user_lon = update.message.location.longitude
        
        # Find stations within 10km
        nearby_stations = data_manager.find_stations_near_location(user_lat, user_lon, 10)
        
        if nearby_stations:
            # Sort by best price for benzina 95
            benzina_stations = [s for s in nearby_stations if s.get('Precio_Gasolina_95_E5')]
            benzina_stations.sort(key=lambda x: (x.get('Precio_Gasolina_95_E5', 999), x['distance']))
            
            messages = []
            for i, station in enumerate(benzina_stations[:5]):
                price = station.get('Precio_Gasolina_95_E5', 'N/A')
                distance = station['distance']
                messages.append(
                    f"{'🥇' if i == 0 else '🔸'} *{station['Rotulo']}*\n"
                    f"📍 {distance}km - {station['Direccion']}\n"
                    f"⛽ Benzina 95: *{price}€*"
                )
            
            result_text = f"🎯 *5 estacions més properes amb millor preu:*\n\n" + "\n\n".join(messages)
            
            await update.message.reply_text(
                result_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(B5, callback_data=str(INICI))
                ]])
            )
        else:
            await update.message.reply_text(
                "❌ No s'han trobat estacions prop teu.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(B5, callback_data=str(INICI))
                ]])
            )
    
    return NIVELL1

@error_handler
async def price_alerts(update: Update, context: CallbackContext):
    """Handler for price alerts feature."""
    query = update.callback_query
    await query.answer()

    button5 = InlineKeyboardButton(B5, callback_data=str(INICI))
    button28 = InlineKeyboardButton(B28, callback_data=str(ALERT_CREATE))
    button29 = InlineKeyboardButton(B29, callback_data=str(ALERT_REMOVE))
    button30 = InlineKeyboardButton(B30, callback_data=str(ALERT_LIST))

    await query.edit_message_text(
        text=M_ALERT_SELECT, parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [button28],
            [button30, button29],
            [button5]
        ])
    )
    return NIVELL2

@error_handler
async def create_alert_fuel_selection(update: Update, context: CallbackContext):
    """Select fuel type for creating alert."""
    query = update.callback_query
    await query.answer()

    button5 = InlineKeyboardButton(B5, callback_data=str(ALERTS))
    
    await query.edit_message_text(
        text="🔔 *Selecciona el combustible per l'alerta:*",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(B8, callback_data=str(ALERT_CREATE_BENZINA))],
            [InlineKeyboardButton(B9, callback_data=str(ALERT_CREATE_GASOLIA))],
            [InlineKeyboardButton(B10, callback_data=str(ALERT_CREATE_GASOLIB))],
            [InlineKeyboardButton(B11, callback_data=str(ALERT_CREATE_GASOLIP))],
            [InlineKeyboardButton(B12, callback_data=str(ALERT_CREATE_GLP))],
            [button5]
        ])
    )
    return NIVELL3

@error_handler
async def create_alert_price_input(update: Update, context: CallbackContext):
    """Handle fuel selection and ask for price threshold."""
    query = update.callback_query
    await query.answer()
    
    fuel_type = query.data.split('_')[2]  # ALERT_CREATE_BENZINA -> BENZINA
    context.user_data['alert_fuel'] = fuel_type
    
    fuel_names = {
        'BENZINA': 'Benzina 95 E5',
        'GASOLIA': 'Gasoli A',
        'GASOLIB': 'Gasoli B', 
        'GASOLIP': 'Gasoli Premium',
        'GLP': 'GLP'
    }
    
    await query.edit_message_text(
        f"🔔 *{fuel_names[fuel_type]}*\n\n"
        "Escriu el preu màxim en euros (ex: 1.45) per rebre una alerta quan el preu baixi d'aquest límit:",
        parse_mode=ParseMode.MARKDOWN
    )
    
    return NIVELL3

@error_handler
async def handle_alert_price(update: Update, context: CallbackContext):
    """Handle price input for alert creation."""
    try:
        price_threshold = float(update.message.text.replace(',', '.'))
        fuel_type = context.user_data.get('alert_fuel')
        
        if not fuel_type:
            await update.message.reply_text("❌ Error: tipus de combustible no trobat.")
            return NIVELL1
            
        user_id = update.message.from_user.id
        username = update.message.from_user.username or update.message.from_user.first_name
        
        # Create the alert
        success = data_manager.add_price_alert(user_id, username, fuel_type, price_threshold)
        
        if success:
            fuel_names = {
                'BENZINA': 'Benzina 95 E5',
                'GASOLIA': 'Gasoli A',
                'GASOLIB': 'Gasoli B', 
                'GASOLIP': 'Gasoli Premium',
                'GLP': 'GLP'
            }
            
            await update.message.reply_text(
                f"✅ Alerta creada!\n\n"
                f"🔔 *{fuel_names[fuel_type]}*\n"
                f"💶 Preu límit: *{price_threshold}€*\n\n"
                "Rebràs una notificació quan alguna estació ofereixi aquest combustible a aquest preu o menys.",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(B5, callback_data=str(INICI))
                ]])
            )
        else:
            await update.message.reply_text(
                "❌ Error creant l'alerta. Torna-ho a intentar.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(B5, callback_data=str(INICI))
                ]])
            )
            
    except ValueError:
        await update.message.reply_text(
            "❌ Preu no vàlid. Escriu un número vàlid (ex: 1.45):",
            parse_mode=ParseMode.MARKDOWN
        )
        return NIVELL3
    
    return NIVELL1

@error_handler
async def list_user_alerts(update: Update, context: CallbackContext):
    """List user's active alerts."""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    subscriptions = data_manager.get_user_subscriptions(user_id)
    
    button5 = InlineKeyboardButton(B5, callback_data=str(ALERTS))
    
    if subscriptions.empty:
        await query.edit_message_text(
            "📋 No tens cap alerta activa.",
            reply_markup=InlineKeyboardMarkup([[button5]])
        )
    else:
        fuel_names = {
            'BENZINA': 'Benzina 95 E5',
            'GASOLIA': 'Gasoli A',
            'GASOLIB': 'Gasoli B', 
            'GASOLIP': 'Gasoli Premium',
            'GLP': 'GLP'
        }
        
        alerts_text = "📋 *Les teves alertes actives:*\n\n"
        for _, alert in subscriptions.iterrows():
            fuel_name = fuel_names.get(alert['fuel_type'], alert['fuel_type'])
            town_text = f" - {alert['town']}" if alert['town'] else ""
            alerts_text += f"🔔 {fuel_name}{town_text}\n💶 Límit: *{alert['price_threshold']}€*\n\n"
        
        await query.edit_message_text(
            alerts_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[button5]])
        )
    
    return NIVELL1

async def check_and_send_alerts(context: CallbackContext):
    """Check for price alerts and send notifications."""
    logger.info("Checking price alerts...")
    
    alerts_to_send = data_manager.check_price_alerts()
    
    for alert in alerts_to_send:
        try:
            fuel_names = {
                'BENZINA': 'Benzina 95 E5',
                'GASOLIA': 'Gasoli A',
                'GASOLIB': 'Gasoli B', 
                'GASOLIP': 'Gasoli Premium',
                'GLP': 'GLP'
            }
            
            fuel_name = fuel_names.get(alert['fuel_type'], alert['fuel_type'])
            town_text = f" a {alert['town']}" if alert['town'] else ""
            
            station_info = ""
            for station in alert['stations'][:3]:
                station_info += f"⛽ *{station['Rotulo']}* - {station['Direccion']}\n"
            
            message = (
                f"🔔 *ALERTA DE PREU!*\n\n"
                f"💰 {fuel_name}{town_text} ara costa *{alert['current_price']}€*\n"
                f"🎯 El teu límit era: {alert['price_threshold']}€\n\n"
                f"📍 *Estacions amb aquest preu:*\n{station_info}"
            )
            
            await context.bot.send_message(
                chat_id=alert['user_id'],
                text=message,
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            logger.error(f"Error sending alert to user {alert['user_id']}: {e}")

# Admin commands
ADMIN_USER_IDS = []  # Add your admin user IDs here
# To become an admin:
# 1. Start the bot and send /start 
# 2. Check the logs to see your user_id being tracked
# 3. Add your user_id to the ADMIN_USER_IDS list above
# 4. Restart the bot
# Example: ADMIN_USER_IDS = [123456789, 987654321]

def is_admin(user_id):
    """Check if user is an admin."""
    return user_id in ADMIN_USER_IDS

@error_handler
async def admin_stats(update: Update, context: CallbackContext):
    """Show user statistics to admin users."""
    if not is_admin(update.message.from_user.id):
        await update.message.reply_text("❌ No tens permisos per executar aquesta comanda.")
        return
    
    stats = data_manager.get_user_stats()
    
    stats_message = (
        f"📊 *Estadístiques del Bot*\n\n"
        f"👥 Total usuaris: *{stats.get('total_users', 0)}*\n"
        f"📅 Actius avui: *{stats.get('today_active', 0)}*\n"
        f"📅 Actius setmana: *{stats.get('week_active', 0)}*\n"
        f"📅 Actius mes: *{stats.get('month_active', 0)}*\n"
        f"🔄 Total interaccions: *{stats.get('total_interactions', 0)}*\n"
        f"📈 Mitjana interaccions/usuari: *{stats.get('avg_interactions_per_user', 0)}*"
    )
    
    await update.message.reply_text(stats_message, parse_mode=ParseMode.MARKDOWN)

@error_handler
async def admin_top_users(update: Update, context: CallbackContext):
    """Show top users to admin users."""
    if not is_admin(update.message.from_user.id):
        await update.message.reply_text("❌ No tens permisos per executar aquesta comanda.")
        return
    
    top_users = data_manager.get_top_users(10)
    
    if not top_users:
        await update.message.reply_text("📊 No hi ha dades d'usuaris disponibles.")
        return
    
    message = "🏆 *Top 10 Usuaris Més Actius*\n\n"
    
    for i, (user_id, username, first_name, interaction_count, last_seen) in enumerate(top_users, 1):
        name = username or first_name or f"User{user_id}"
        last_seen_str = last_seen.strftime("%d/%m/%Y") if last_seen else "Desconegut"
        
        message += f"{i}. *{name}*\n"
        message += f"   Interaccions: {interaction_count}\n"
        message += f"   Última visita: {last_seen_str}\n\n"
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

@error_handler
async def admin_user_info(update: Update, context: CallbackContext):
    """Get detailed info about a specific user."""
    if not is_admin(update.message.from_user.id):
        await update.message.reply_text("❌ No tens permisos per executar aquesta comanda.")
        return
    
    if len(context.args) != 1:
        await update.message.reply_text("ℹ️ Ús: /userinfo <user_id>")
        return
    
    try:
        user_id = int(context.args[0])
        user_info = data_manager.get_user_info(user_id)
        
        if not user_info:
            await update.message.reply_text(f"❌ Usuari {user_id} no trobat.")
            return
        
        message = (
            f"👤 *Informació d'Usuari*\n\n"
            f"🆔 ID: `{user_info['user_id']}`\n"
            f"👤 Username: {user_info['username'] or 'N/A'}\n"
            f"📝 Nom: {user_info['first_name'] or 'N/A'}\n"
            f"🌐 Idioma: {user_info['language_code'] or 'N/A'}\n"
            f"📅 Primera visita: {user_info['first_seen'].strftime('%d/%m/%Y %H:%M') if user_info['first_seen'] else 'N/A'}\n"
            f"📅 Última visita: {user_info['last_seen'].strftime('%d/%m/%Y %H:%M') if user_info['last_seen'] else 'N/A'}\n"
            f"🔄 Interaccions: {user_info['interaction_count']}\n"
            f"🔔 Alertes actives: {user_info['active_alerts']}\n"
            f"✅ Actiu: {'Sí' if user_info['is_active'] else 'No'}"
        )
        
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
        
    except ValueError:
        await update.message.reply_text("❌ ID d'usuari no vàlid. Ha de ser un número.")

@error_handler
async def privacy_delete(update: Update, context: CallbackContext):
    """Allow users to delete their data for GDPR compliance."""
    user_id = update.message.from_user.id
    username = update.message.from_user.username or update.message.from_user.first_name
    
    # Deactivate user and their data
    success = data_manager.deactivate_user(user_id)
    
    if success:
        await update.message.reply_text(
            "✅ Les teves dades han estat eliminades del sistema.\n\n"
            "Això inclou:\n"
            "• El teu perfil d'usuari\n"
            "• Totes les teves alertes de preu\n"
            "• Historial d'interaccions\n\n"
            "Pots continuar usant el bot, però es crearà un nou perfil si ho fas.",
            parse_mode=ParseMode.MARKDOWN
        )
        logger.info(f"User {user_id} ({username}) requested data deletion")
    else:
        await update.message.reply_text(
            "❌ Hi ha hagut un error eliminant les teves dades. Torna-ho a intentar més tard."
        )

@error_handler
async def refresh_data(context: CallbackContext):
    """Refreshes the data from the database."""
    logger.info("Refreshing data...")
    data_manager.load_data()

def get_conv_handler():
    return ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NIVELL0: [
                CallbackQueryHandler(start_over, pattern=f"^{INICI}$")
            ],
            NIVELL1: [
                CallbackQueryHandler(preu, pattern=f"^{PREU}$"),
                CallbackQueryHandler(tipus_combustible, pattern=f"^{COMBUSTIBLE}$"),
                CallbackQueryHandler(per_municipi, pattern=f"^{POBLE}$"),
                CallbackQueryHandler(info, pattern=f"^{INFO}$"),
                CallbackQueryHandler(price_charts, pattern=f"^{CHARTS}$"),
                CallbackQueryHandler(location_search, pattern=f"^{LOCATION}$"),
                CallbackQueryHandler(price_alerts, pattern=f"^{ALERTS}$"),
                CallbackQueryHandler(start_over, pattern=f"^{INICI}$")
            ],
            NIVELL2: [
                CallbackQueryHandler(mes_barates, pattern=f"^{BARATES}$"),
                CallbackQueryHandler(mes_cares, pattern=f"^{CARES}$"),
                CallbackQueryHandler(preu, pattern=f"^{PREU}$"),
                CallbackQueryHandler(start_over, pattern=f"^{INICI}$"),
                CallbackQueryHandler(fuel_info, pattern=f"^{FUEL_PREFIX}"),
                CallbackQueryHandler(town_info, pattern=f"^{TOWN_PREFIX}"),
                CallbackQueryHandler(price_charts, pattern=f"^{CHARTS}$"),
                CallbackQueryHandler(price_charts, pattern=f"^{CHART_FUEL_PREFIX}"),
                CallbackQueryHandler(generate_chart, pattern=f"^{CHART_PREFIX}"),
                CallbackQueryHandler(create_alert_fuel_selection, pattern=f"^{ALERT_CREATE}$"),
                CallbackQueryHandler(list_user_alerts, pattern=f"^{ALERT_LIST}$"),
                CallbackQueryHandler(price_alerts, pattern=f"^{ALERTS}$"),
                MessageHandler(filters.LOCATION, handle_location),
            ],
            NIVELL3: [
                CallbackQueryHandler(create_alert_price_input, pattern=f"^{ALERT_CREATE}_"),
                CallbackQueryHandler(price_alerts, pattern=f"^{ALERTS}$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_alert_price),
            ],
        },
        fallbacks=[CommandHandler('start', start)],
        name="conversacio",
        persistent=True,
    )

def main():
    persistence_filepath = '/home/damia/Bot_Menorca_EESS/persistencia_arxiu'
    
    try:
        persistencia = PicklePersistence(filepath=persistence_filepath)
    except (EOFError, TypeError):
        print(f"Error unpickling the persistence file: {persistence_filepath}. Removing corrupted file.")
        os.remove(persistence_filepath)
        persistencia = PicklePersistence(filepath=persistence_filepath)

    # Initialize data manager
    try:
        logger.info("Initializing data manager...")
        data_manager.load_data()
    except Exception as e:
        logger.critical(f"FATAL: Could not load initial data. The bot cannot start. Error: {e}")
        return

    application = Application.builder().token(secret.secret["bot_token"]).persistence(persistencia).build()

    # Add job to refresh data every 10 minutes
    job_queue = application.job_queue
    job_queue.run_repeating(refresh_data, interval=datetime.timedelta(minutes=10), first=0)
    
    # Add job to check price alerts every hour
    job_queue.run_repeating(check_and_send_alerts, interval=datetime.timedelta(hours=1), first=0)

    conv_handler = get_conv_handler()

    # Main handlers
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('start', start))
    application.add_handler(InlineQueryHandler(inlinequery))
    
    # Admin commands
    application.add_handler(CommandHandler('stats', admin_stats))
    application.add_handler(CommandHandler('topusers', admin_top_users))
    application.add_handler(CommandHandler('userinfo', admin_user_info))
    
    # Privacy command
    application.add_handler(CommandHandler('deletemydata', privacy_delete))

    application.run_polling()

if __name__ == '__main__':
    main()
