import os
from telegram.ext import Application, CommandHandler, ConversationHandler, CallbackQueryHandler, CallbackContext, PicklePersistence, InlineQueryHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.constants import ParseMode
import extractor_dades
import logging
import last_update
import secret
from uuid import uuid4

logging.basicConfig(filename="/home/combustible/logs/main_bot.log", format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.DEBUG)


m_instruct = "▪️*Selecciona una opció :*"

b1 = '💶 Per PREU'
b2 = '🚗🚜 Per COMBUSTIBLE'
b3 = '🏘 Per POBLE'
b4 = '👁‍🗨 +INFO'
b5 = '🔙 Enrrere'
b6 = '✅ 5 més barates'
b7 = '‼️ 5 més cares'
b8 = '🟢 Benzina 95 E5'
b9 = '⚫️ Gasoli A'
b10= '🟡 Gasoli B'
b11= '🟠 Gasoli Premium'
b12= '⚪️ GLP'
b13='MAÓ'
b14='CIUTADELLA'
b15='ALAIOR'
b16='ES MERCADAL'
b17='FERRERIES'
b18='SANT LLUÍS'
b19='ES CASTELL'
b20='FORNELLS'

userId = None
chatID = None



NIVELL0, NIVELL1, NIVELL2 = range(3)

PREU, COMBUSTIBLE, POBLE, INFO, BARATES, CARES, INICI, GASOLIB, GASOLIA, GASOLIP, BENZINA, GLP, P1, P2, P3, P4, P5, P6, P7, P8 = range(20)


async def start(update: Update, context: CallbackContext):
    userId = str(update.message.from_user.username)
    await update.message.reply_text("Benvingut *{}*.\nMés ⛽️ per menys 💶!\n"\
    "Preus actualitzats cada 10 minuts.".format(userId.upper()), parse_mode=ParseMode.MARKDOWN, disable_web_page_preview= True,)

    button1 = InlineKeyboardButton(
        b1, callback_data=str(PREU)
    )
    button2 = InlineKeyboardButton(
        b2, callback_data=str(COMBUSTIBLE)
    )
    button3 = InlineKeyboardButton(
        b3, callback_data=str(POBLE)
    )
    button4 = InlineKeyboardButton(
        b4, callback_data=str(INFO)
    )

    await update.message.reply_text(
            text = m_instruct, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview= True,
            reply_markup = InlineKeyboardMarkup([
                [button1, button2],
                [button3, button4]
            ])
        )
    return NIVELL1

async def start_over(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    button1 = InlineKeyboardButton(
        b1, callback_data=str(PREU)
    )
    button2 = InlineKeyboardButton(
        b2, callback_data=str(COMBUSTIBLE)
    )
    button3 = InlineKeyboardButton(
        b3, callback_data=str(POBLE)
    )
    button4 = InlineKeyboardButton(
        b4, callback_data=str(INFO)
    )

    await query.edit_message_text(
            text = m_instruct, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview= True,
            reply_markup = InlineKeyboardMarkup([
                [button1, button2],
                [button3, button4]
            ])
        )
    return NIVELL1

async def preu(update: Update, context: CallbackContext):
    global userId, chatID
    query = update.callback_query
    userId = str(query.from_user.username)
    chatID = str(query.from_user.id)
    #await db_users(update, context)
    await query.answer()
    button5 = InlineKeyboardButton(
        b5, callback_data=str(INICI)
    )
    button6 = InlineKeyboardButton(
        b6, callback_data=str(BARATES)
    )
    button7 = InlineKeyboardButton(
        b7, callback_data=str(CARES)
    )
    missatge_preu= '*SELECCIONA :*'
    await query.edit_message_text(
    text= missatge_preu, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview= True,
    reply_markup = InlineKeyboardMarkup([
        [button6, button7],
        [button5]
        ])
    )
    return NIVELL2

async def mes_barates(update, context=CallbackContext):
    output_barates = extractor_dades.estacions_servei_extraccio_benzina_ascendent()

    def format_location(lat, long):
        return 'https://www.google.com/maps/@{},{},20z'.format(lat.replace(',', '.'), long.replace(',', '.'))

    available_stations = min(len(output_barates), 5)
    locations = [format_location(est[5], est[6]) for est in output_barates[:available_stations]]

    query = update.callback_query
    await query.answer()
    
    button5 = InlineKeyboardButton(b5, callback_data=str(PREU))

    missatge_preu = "\n\n".join(
        [
            "🔸*{}*\n[{}]({})\n{}\nBenzina 95 E5 = *{}*€\nDiesel A = *{}*€.".format(
                est[1], est[4], loc, est[0], est[2], est[3]
            ) if i % 2 == 0 else
            "🔹*{}*\n[{}]({})\n{}\nBenzina 95 E5 = *{}*€\nDiesel A = *{}*€.".format(
                est[1], est[4], loc, est[0], est[2], est[3]
            )
            for i, (est, loc) in enumerate(zip(output_barates[:available_stations], locations))
        ]
    )

    await query.edit_message_text(
        text=missatge_preu, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([[button5]])
    )

    return NIVELL1


async def mes_barates_inlinequery(update: Update, context=CallbackContext):
    output_barates = extractor_dades.estacions_servei_extraccio_benzina_ascendent()

    def format_location(lat, long):
        return 'https://www.google.com/maps/@{},{},20z'.format(lat.replace(',', '.'), long.replace(',', '.'))

    available_stations = min(len(output_barates), 5)
    locations = [format_location(est[5], est[6]) for est in output_barates[:available_stations]]

    missatge_preu = "**MÉS BARATES**\n\n" + "\n\n".join(
        [
            "🔸*{}*\n[{}]({})\n{}\nBenzina 95 E5 = *{}*€\nDiesel A = *{}*€.".format(
                est[1], est[4], loc, est[0], est[2], est[3]
            ) if i % 2 == 0 else
            "🔹*{}*\n[{}]({})\n{}\nBenzina 95 E5 = *{}*€\nDiesel A = *{}*€.".format(
                est[1], est[4], loc, est[0], est[2], est[3]
            )
            for i, (est, loc) in enumerate(zip(output_barates[:available_stations], locations))
        ]
    )
    
    return missatge_preu
    
async def mes_cares(update: Update, context=CallbackContext):
    output_cares = extractor_dades.estacions_servei_extraccio_benzina_descendent()

    def format_location(lat, long):
        return 'https://www.google.com/maps/@{},{},20z'.format(lat.replace(',', '.'), long.replace(',', '.'))

    available_stations = min(len(output_cares), 5)
    locations = [format_location(est[5], est[6]) for est in output_cares[:available_stations]]

    query = update.callback_query
    await query.answer()
    
    button5 = InlineKeyboardButton(b5, callback_data=str(PREU))

    missatge_preu = "\n\n".join(
        [
            "🔸*{}*\n[{}]({})\n{}\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.".format(
                est[1], est[4], loc, est[0], est[2], est[3]
            ) if i % 2 == 0 else
            "🔹*{}*\n[{}]({})\n{}\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.".format(
                est[1], est[4], loc, est[0], est[2], est[3]
            )
            for i, (est, loc) in enumerate(zip(output_cares[:available_stations], locations))
        ]
    )

    await query.edit_message_text(
        text=missatge_preu, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([[button5]])
    )

    return NIVELL1

async def mes_cares_inlinequery(update: Update, context=CallbackContext):
    output_cares = extractor_dades.estacions_servei_extraccio_benzina_descendent()

    def format_location(lat, long):
        return 'https://www.google.com/maps/@{},{},20z'.format(lat.replace(',', '.'), long.replace(',', '.'))

    available_stations = min(len(output_cares), 5)
    locations = [format_location(est[5], est[6]) for est in output_cares[:available_stations]]

    missatge_preu = "*MÉS CARES*\n\n" + "\n\n".join(
        [
            "🔸*{}*\n[{}]({})\n{}\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.".format(
                est[1], est[4], loc, est[0], est[2], est[3]
            ) if i % 2 == 0 else
            "🔹*{}*\n[{}]({})\n{}\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.".format(
                est[1], est[4], loc, est[0], est[2], est[3]
            )
            for i, (est, loc) in enumerate(zip(output_cares[:available_stations], locations))
        ]
    )

    return missatge_preu

async def tipus_combustible(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    button5 = InlineKeyboardButton(
        b5, callback_data=str(INICI)
    )
    button8 = InlineKeyboardButton(
        b8, callback_data=str(BENZINA)
    )
    button9 = InlineKeyboardButton(
        b9, callback_data=str(GASOLIA)
    )
    button10 = InlineKeyboardButton(
        b10, callback_data=str(GASOLIB)
    )
    button11 = InlineKeyboardButton(
        b11, callback_data=str(GASOLIP)
    )
    button12 = InlineKeyboardButton(
        b12, callback_data=str(GLP)
    )
    missatge_preu= '*SELECCIONA :*'
    await query.edit_message_text(
    text= missatge_preu, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview= True,
    reply_markup = InlineKeyboardMarkup([
        [button8,button9],
        [button10,button11],
        [button12,button5]
        ])
    )
    return NIVELL2

async def benzina(update: Update, context=CallbackContext):
    output_benzina = extractor_dades.estacions_servei_extraccio_benzina_ascendent()

    available_stations = min(len(output_benzina), 21)

    query = update.callback_query
    await query.answer()
    
    button5 = InlineKeyboardButton(b5, callback_data=str(COMBUSTIBLE))

    missatge_preu = "\n\n".join(
        [
            "🔸*{}*\n{}\n{}\nBenzina 95 E5 *{}*€.".format(
                est[1], est[4], est[0], est[2]
            ) if i % 2 == 0 else
            "🔹*{}*\n{}\n{}\nBenzina 95 E5 *{}*€.".format(
                est[1], est[4], est[0], est[2]
            )
            for i, est in enumerate(output_benzina[:available_stations])
        ]
    )

    await query.edit_message_text(
        text=missatge_preu, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([[button5]])
    )

    return NIVELL1


async def gasoli_A(update: Update, context: CallbackContext):
    output_gasoliA = extractor_dades.carburants_extraccio_diesel_A_ascendent()

    available_stations = min(len(output_gasoliA), 21)

    query = update.callback_query
    await query.answer()
    
    button5 = InlineKeyboardButton(b5, callback_data=str(COMBUSTIBLE))

    missatge_gasoliA = "\n\n".join(
        [
            "🔸*{}*\n{}\n{}\nGasoli A *{}*€.".format(
                est[1], est[3], est[0], est[2]
            ) if i % 2 == 0 else
            "🔹*{}*\n{}\n{}\nGasoli A *{}*€.".format(
                est[1], est[3], est[0], est[2]
            )
            for i, est in enumerate(output_gasoliA[:available_stations])
        ]
    )

    await query.edit_message_text(
        text=missatge_gasoliA, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([[button5]])
    )

    return NIVELL1

async def gasoli_B(update: Update, context: CallbackContext):
    output_gasoliB = extractor_dades.carburants_extraccio_diesel_B_ascendent()

    available_stations = min(len(output_gasoliB), 2)

    query = update.callback_query
    await query.answer()
    
    button5 = InlineKeyboardButton(b5, callback_data=str(COMBUSTIBLE))

    missatge_gasoliB = "\n\n".join(
        [
            "🔸*{}*\n{}\n{}\nGasoli A *{}*€.".format(
                est[1], est[3], est[0], est[2]
            ) if i % 2 == 0 else
            "🔹*{}*\n{}\n{}\nGasoli A *{}*€.".format(
                est[1], est[3], est[0], est[2]
            )
            for i, est in enumerate(output_gasoliB[:available_stations])
        ]
    )

    await query.edit_message_text(
        text=missatge_gasoliB, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([[button5]])
    )

    return NIVELL1

async def gasoli_Premium(update: Update, context: CallbackContext):
    output_gasoliP = extractor_dades.carburants_extraccio_diesel_premium_ascendent()

    available_stations = min(len(output_gasoliP), 4)

    query = update.callback_query
    await query.answer()
    
    button5 = InlineKeyboardButton(b5, callback_data=str(COMBUSTIBLE))

    missatge_gasoliP = "\n\n".join(
        [
            "🔸*{}*\n{}\n{}\nGasoli Premium *{}*€.".format(
                est[1], est[3], est[0], est[2]
            ) if i % 2 == 0 else
            "🔹*{}*\n{}\n{}\nGasoli Premium *{}*€.".format(
                est[1], est[3], est[0], est[2]
            )
            for i, est in enumerate(output_gasoliP[:available_stations])
        ]
    )

    await query.edit_message_text(
        text=missatge_gasoliP, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([[button5]])
    )

    return NIVELL1

async def GL_Petroli(update: Update, context: CallbackContext):
    output_GLP = extractor_dades.carburants_extraccio_GLP_ascendent()

    available_stations = min(len(output_GLP), 2)

    query = update.callback_query
    await query.answer()
    
    button5 = InlineKeyboardButton(b5, callback_data=str(COMBUSTIBLE))

    missatge_GLP = "\n\n".join(
        [
            "🔸*{}*\n{}\n{}\nGLP *{}*€.".format(
                est[1], est[3], est[0], est[2]
            ) if i % 2 == 0 else
            "🔹*{}*\n{}\n{}\nGLP *{}*€.".format(
                est[1], est[3], est[0], est[2]
            )
            for i, est in enumerate(output_GLP[:available_stations])
        ]
    )

    await query.edit_message_text(
        text=missatge_GLP, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([[button5]])
    )

    return NIVELL1

async def per_municipi(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    button5 = InlineKeyboardButton(
        b5, callback_data=str(INICI)
    )
    button13 = InlineKeyboardButton(
        b13, callback_data=str(P1)
    )
    button14 = InlineKeyboardButton(
        b14, callback_data=str(P2)
    )
    button15 = InlineKeyboardButton(
        b15, callback_data=str(P3)
    )
    button16 = InlineKeyboardButton(
        b16, callback_data=str(P4)
    )
    button17 = InlineKeyboardButton(
        b17, callback_data=str(P5)
    )
    button18 = InlineKeyboardButton(
        b18, callback_data=str(P6)
    )
    button19 = InlineKeyboardButton(
        b19, callback_data=str(P7)
    )
    button20 = InlineKeyboardButton(
        b20, callback_data=str(P8)
    )
    await query.edit_message_text(
            text = m_instruct, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview= True,
            reply_markup = InlineKeyboardMarkup([
                [button13, button14, button15],
                [button16, button17, button18],
                [button19, button20, button5]
            ])
        )
    return NIVELL2

async def mao(update: Update, context: CallbackContext):
    output_mao = extractor_dades.extraccio_MAO_ascendent()

    def format_location(lat, long):
        return 'https://www.google.com/maps/@{},{},20z'.format(lat.replace(',', '.'), long.replace(',', '.'))

    available_stations = min(len(output_mao), 7)
    locations = [format_location(est[5], est[6]) for est in output_mao[:available_stations]]

    query = update.callback_query
    await query.answer()
    
    button5 = InlineKeyboardButton(b5, callback_data=str(POBLE))

    missatge_mao = "\n\n".join(
        [
            "🔸*{}*\n[{}]({})\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.".format(
                est[1], est[4], loc, est[2], est[3]
            ) if i % 2 == 0 else
            "🔹*{}*\n[{}]({})\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.".format(
                est[1], est[4], loc, est[2], est[3]
            )
            for i, (est, loc) in enumerate(zip(output_mao[:available_stations], locations))
        ]
    )

    await query.edit_message_text(
        text=missatge_mao, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([[button5]])
    )

    return NIVELL1

async def ciutadella(update: Update, context: CallbackContext):
    output_ciutadella = extractor_dades.extraccio_CIUTADELLA_ascendent()

    def format_location(lat, long):
        return 'https://www.google.com/maps/@{},{},20z'.format(lat.replace(',', '.'), long.replace(',', '.'))

    available_stations = min(len(output_ciutadella), 5)
    locations = [format_location(est[5], est[6]) for est in output_ciutadella[:available_stations]]

    query = update.callback_query
    await query.answer()
    
    button5 = InlineKeyboardButton(b5, callback_data=str(POBLE))

    missatge_ciutadella = "\n\n".join(
        [
            "🔸*{}*\n[{}]({})\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.".format(
                est[1], est[4], loc, est[2], est[3]
            ) if i % 2 == 0 else
            "🔹*{}*\n[{}]({})\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.".format(
                est[1], est[4], loc, est[2], est[3]
            )
            for i, (est, loc) in enumerate(zip(output_ciutadella[:available_stations], locations))
        ]
    )

    await query.edit_message_text(
        text=missatge_ciutadella, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([[button5]])
    )

    return NIVELL1

async def alaior(update: Update, context: CallbackContext):
    output_alaior = extractor_dades.extraccio_ALAIOR_ascendent()

    def format_location(lat, long):
        return 'https://www.google.com/maps/@{},{},20z'.format(lat.replace(',', '.'), long.replace(',', '.'))

    available_stations = min(len(output_alaior), 3)
    locations = [format_location(est[5], est[6]) for est in output_alaior[:available_stations]]

    query = update.callback_query
    await query.answer()
    
    button5 = InlineKeyboardButton(b5, callback_data=str(POBLE))

    missatge_alaior = "\n\n".join(
        [
            "🔸*{}*\n[{}]({})\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.".format(
                est[1], est[4], loc, est[2], est[3]
            ) if i % 2 == 0 else
            "🔹*{}*\n[{}]({})\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.".format(
                est[1], est[4], loc, est[2], est[3]
            )
            for i, (est, loc) in enumerate(zip(output_alaior[:available_stations], locations))
        ]
    )

    await query.edit_message_text(
        text=missatge_alaior, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([[button5]])
    )

    return NIVELL1

async def ferreries(update: Update, context: CallbackContext):
    output_ferreries = extractor_dades.extraccio_FERRERIES_ascendent()
    
    query = update.callback_query
    await query.answer()
    button5 = InlineKeyboardButton(b5, callback_data=str(POBLE))

    if len(output_ferreries) > 0:
        adequacio_lat = str.replace(output_ferreries[0][5], ',', '.')
        adequacio_long = str.replace(output_ferreries[0][6], ',', '.')
        ubicacio = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat, adequacio_long)

        missatge_ferreries = "🔸*{}*\n[{}]({})\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.".format(
            output_ferreries[0][1], output_ferreries[0][4], ubicacio, output_ferreries[0][2], output_ferreries[0][3]
        )
    else:
        missatge_ferreries = "😨❌No disponible en aquests moments"

    await query.edit_message_text(
        text=missatge_ferreries, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([[button5]])
    )
    
    return NIVELL1

async def mercadal(update: Update, context: CallbackContext):
    output_merdal = extractor_dades.extraccio_MERDAL_ascendent()

    def format_location(lat, long):
        return 'https://www.google.com/maps/@{},{},20z'.format(lat.replace(',', '.'), long.replace(',', '.'))

    available_stations = min(len(output_merdal), 2)
    locations = [format_location(est[5], est[6]) for est in output_merdal[:available_stations]]

    query = update.callback_query
    await query.answer()
    
    button5 = InlineKeyboardButton(b5, callback_data=str(POBLE))

    missatge_merdal = "\n\n".join(
        [
            "🔸*{}*\n[{}]({})\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.".format(
                est[1], est[4], loc, est[2], est[3]
            ) if i % 2 == 0 else
            "🔹*{}*\n[{}]({})\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.".format(
                est[1], est[4], loc, est[2], est[3]
            )
            for i, (est, loc) in enumerate(zip(output_merdal[:available_stations], locations))
        ]
    )

    await query.edit_message_text(
        text=missatge_merdal, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([[button5]])
    )

    return NIVELL1

async def santlluis(update: Update, context: CallbackContext):
    output_santlluis = extractor_dades.extraccio_SANTLLUIS_ascendent()

    def format_location(lat, long):
        return 'https://www.google.com/maps/@{},{},20z'.format(lat.replace(',', '.'), long.replace(',', '.'))

    available_stations = min(len(output_santlluis), 2)
    locations = [format_location(est[5], est[6]) for est in output_santlluis[:available_stations]]

    query = update.callback_query
    await query.answer()
    
    button5 = InlineKeyboardButton(b5, callback_data=str(POBLE))

    missatge_santlluis = "\n\n".join(
        [
            "🔹*{}*\n[{}]({})\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.".format(
                est[1], est[4], loc, est[2], est[3]
            ) if i % 2 == 0 else
            "🔸*{}*\n[{}]({})\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.".format(
                est[1], est[4], loc, est[2], est[3]
            )
            for i, (est, loc) in enumerate(zip(output_santlluis[:available_stations], locations))
        ]
    )

    await query.edit_message_text(
        text=missatge_santlluis, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([[button5]])
    )

    return NIVELL1

async def fornells(update: Update, context: CallbackContext):
    output_fornells = extractor_dades.extraccio_FORNELLS_ascendent()

    query = update.callback_query
    await query.answer()
    button5 = InlineKeyboardButton(b5, callback_data=str(POBLE))

    if len(output_fornells) > 0:
        adequacio_lat = 39.9787575
        adequacio_long = 4.194645
        ubicacio = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat, adequacio_long)

        missatge_fornells = "🔸*{}*\n[{}]({})\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.".format(
            output_fornells[0][0], output_fornells[0][1], ubicacio, output_fornells[0][2], output_fornells[0][3]
        )
    else:
        missatge_fornells = "😨❌No disponible en aquests moments"

    await query.edit_message_text(
        text=missatge_fornells, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([[button5]])
    )

    return NIVELL1
    
async def escastell(update: Update, context: CallbackContext):
    output_escastell = extractor_dades.extraccio_ESCASTELL_ascendent()

    query = update.callback_query
    await query.answer()
    button5 = InlineKeyboardButton(b5, callback_data=str(POBLE))

    if len(output_escastell) > 0:
        adequacio_lat = str.replace(output_escastell[0][5], ',', '.')
        adequacio_long = str.replace(output_escastell[0][6], ',', '.')
        ubicacio = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat, adequacio_long)

        missatge_escastell = "🔸*{}*\n[{}]({})\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.".format(
            output_escastell[0][1], output_escastell[0][4], ubicacio, output_escastell[0][2], output_escastell[0][3]
        )
    else:
        missatge_escastell = "😨❌No disponible en aquests moments"

    await query.edit_message_text(
        text=missatge_escastell, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([[button5]])
    )

    return NIVELL1


async def info(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    button5 = InlineKeyboardButton(
        b5, callback_data=str(INICI)
    )
    missatge_info = "Dades extretes de *Ministerio de Industria, Comercio y Turismo*.\n"\
                    "S'ha comprobat que algunes dades d'ubicació están malament o no son prou precises.\n"\
                    "Ses dades errónees han estat notificades.\n\n"\
                    "*Última actualització de preus:* {}\n\n"\
                    "Escrit per Damia Sintes.\nCodi a [GitHub](https://github.com/Damiasroca/Bot_Menorca_EESS)".format((last_update.last()))
    await query.edit_message_text(
            text = missatge_info, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview= False,
            reply_markup = InlineKeyboardMarkup([
                [button5]
            ])
        )
    return NIVELL1

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


def main():
    persistence_filepath = '/home/combustible/persistencia_arxiu'
    
    try:
        persistencia = PicklePersistence(filepath=persistence_filepath)
    except (EOFError, TypeError):
        print(f"Error unpickling the persistence file: {persistence_filepath}. Removing corrupted file.")
        os.remove(persistence_filepath)
        persistencia = PicklePersistence(filepath=persistence_filepath)

    application = Application.builder().token(secret.secret["bot_token"]).persistence(persistencia).build()


    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NIVELL0: [
                CallbackQueryHandler(start_over, pattern=str(INICI))
            ],
            NIVELL1: [
                CallbackQueryHandler(preu, pattern=str(PREU)),
                CallbackQueryHandler(tipus_combustible, pattern=str(COMBUSTIBLE)),
                CallbackQueryHandler(per_municipi, pattern=str(POBLE)),
                CallbackQueryHandler(info, pattern=str(INFO)),
                CallbackQueryHandler(start_over, pattern=str(INICI))
            ],
            NIVELL2: [
                CallbackQueryHandler(mes_barates, pattern=str(BARATES)),
                CallbackQueryHandler(mes_cares, pattern=str(CARES)),
                CallbackQueryHandler(preu, pattern=str(PREU)),
                CallbackQueryHandler(start_over, pattern=str(INICI)),
                CallbackQueryHandler(benzina, pattern=str(BENZINA)),
                CallbackQueryHandler(gasoli_A, pattern=str(GASOLIA)),
                CallbackQueryHandler(gasoli_B, pattern=str(GASOLIB)),
                CallbackQueryHandler(gasoli_Premium, pattern=str(GASOLIP)),
                CallbackQueryHandler(GL_Petroli, pattern=str(GLP)),
                CallbackQueryHandler(mao, pattern=str(P1)),
                CallbackQueryHandler(ciutadella, pattern=str(P2)),
                CallbackQueryHandler(fornells, pattern=str(P8)),
                CallbackQueryHandler(mercadal, pattern=str(P4)),
                CallbackQueryHandler(alaior, pattern=str(P3)),
                CallbackQueryHandler(escastell, pattern=str(P7)),
                CallbackQueryHandler(santlluis, pattern=str(P6)),
                CallbackQueryHandler(ferreries, pattern=str(P5))
            ],
        },
        fallbacks=[CommandHandler('start_over', start_over)],
        allow_reentry=True,
        name="conversacio",
        persistent=True,
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('start', start))
    application.add_handler(InlineQueryHandler(inlinequery))

    application.run_polling()

if __name__ == '__main__':
    main()
