import telegram
from telegram.ext import Updater, CommandHandler, ConversationHandler, CallbackQueryHandler, CallbackContext, PicklePersistence
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
import extractor_dades
import logging
import last_update
import secret

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)


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



NIVELL0, NIVELL1, NIVELL2 = range(3)

PREU, COMBUSTIBLE, POBLE, INFO, BARATES, CARES, INICI, GASOLIB, GASOLIA, GASOLIP, BENZINA, GLP, P1, P2, P3, P4, P5, P6, P7, P8 = range(20)


def start(update, context):
    global userId
    userId = str(update.message.from_user.username)
    update.message.reply_text("Benvingut *{}*.\nMés ⛽️ per menys 💶!\n"\
    "Preus actualitzats cada 10 minuts.".format(userId.upper()), parse_mode=telegram.ParseMode.MARKDOWN)

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

    update.message.reply_text(
            text = m_instruct, parse_mode=telegram.ParseMode.MARKDOWN,
            reply_markup = InlineKeyboardMarkup([
                [button1, button2],
                [button3, button4]
            ])
        )
    return NIVELL1

def start_over(update: Update, context: CallbackContext):

    query = update.callback_query
    query.answer()

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

    query.edit_message_text(
            text = m_instruct, parse_mode=telegram.ParseMode.MARKDOWN,
            reply_markup = InlineKeyboardMarkup([
                [button1, button2],
                [button3, button4]
            ])
        )
    return NIVELL1

def preu(update, context= CallbackContext):
    query = update.callback_query
    query.answer()
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
    query.edit_message_text(
    text= missatge_preu, parse_mode=telegram.ParseMode.MARKDOWN_V2,
    reply_markup = InlineKeyboardMarkup([
        [button6, button7],
        [button5]
        ])
    )
    return NIVELL2

def mes_barates(update, context = CallbackContext):
    output_barates = extractor_dades.estacions_servei_extraccio_benzina_ascendent()
    try:
        adequacio_lat =  str.replace(output_barates[0][5], ',', '.')
        adequacio_long = str.replace(output_barates[0][6], ',', '.')
        adequacio_lat1 =  str.replace(output_barates[1][5], ',', '.')
        adequacio_long1 = str.replace(output_barates[1][6], ',', '.')
        adequacio_lat2 =  str.replace(output_barates[2][5], ',', '.')
        adequacio_long2 = str.replace(output_barates[2][6], ',', '.')
        adequacio_lat3 =  str.replace(output_barates[3][5], ',', '.')
        adequacio_long3 = str.replace(output_barates[3][6], ',', '.')
        adequacio_lat4 =  str.replace(output_barates[4][5], ',', '.')
        adequacio_long4 = str.replace(output_barates[4][6], ',', '.')
        ubicacio = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat, adequacio_long)
        ubicacio1 = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat1, adequacio_long1)
        ubicacio2 = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat2, adequacio_long2)
        ubicacio3 = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat3, adequacio_long3)
        ubicacio4 = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat4, adequacio_long4)

        query = update.callback_query
        query.answer()
        button5 = InlineKeyboardButton(
            b5, callback_data=str(PREU)
        )
    
        missatge_preu=  "🔸*{}*\n[{}]({})\n{}\nBenzina 95 E5 = *{}*€\nDiesel A =  *{}*€.\n\n"\
                        "🔹*{}*\n[{}]({})\n{}\nBenzina 95 E5 = *{}*€\nDiesel A = *{}*€.\n\n"\
                        "🔸*{}*\n[{}]({})\n{}\nBenzina 95 E5 = *{}*€\nDiesel A = *{}*€.\n\n"\
                        "🔹*{}*\n[{}]({})\n{}\nBenzina 95 E5 = *{}*€\nDiesel A = *{}*€.\n\n"\
                        "🔸*{}*\n[{}]({})\n{}\nBenzina 95 E5 = *{}*€\nDiesel A = *{}*€.".format(
                        (output_barates[0][1]),(output_barates[0][4]),(ubicacio),(output_barates[0][0]),(output_barates[0][2]),(output_barates[0][3]),\
                        (output_barates[1][1]),(output_barates[1][4]),(ubicacio1),(output_barates[1][0]),(output_barates[1][2]),(output_barates[1][3]),\
                        (output_barates[2][1]),(output_barates[2][4]),(ubicacio2),(output_barates[2][0]),(output_barates[2][2]),(output_barates[2][3]),\
                        (output_barates[3][1]),(output_barates[3][4]),(ubicacio3),(output_barates[3][0]),(output_barates[3][2]),(output_barates[3][3]),\
                        (output_barates[4][1]),(output_barates[4][4]),(ubicacio4),(output_barates[4][0]),(output_barates[4][2]),(output_barates[4][3])
                        )
        query.edit_message_text(
        text= missatge_preu, parse_mode=telegram.ParseMode.MARKDOWN,
        reply_markup = InlineKeyboardMarkup([
            [button5]
            ])
        )
        return NIVELL1
    except:
        adequacio_lat =  str.replace(output_barates[0][5], ',', '.')
        adequacio_long = str.replace(output_barates[0][6], ',', '.')
        adequacio_lat1 =  str.replace(output_barates[1][5], ',', '.')
        adequacio_long1 = str.replace(output_barates[1][6], ',', '.')
        adequacio_lat2 =  str.replace(output_barates[2][5], ',', '.')
        adequacio_long2 = str.replace(output_barates[2][6], ',', '.')
        adequacio_lat3 =  str.replace(output_barates[3][5], ',', '.')
        adequacio_long3 = str.replace(output_barates[3][6], ',', '.')
        ubicacio = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat, adequacio_long)
        ubicacio1 = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat1, adequacio_long1)
        ubicacio2 = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat2, adequacio_long2)
        ubicacio3 = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat3, adequacio_long3)

        query = update.callback_query
        query.answer()
        button5 = InlineKeyboardButton(
            b5, callback_data=str(PREU)
        )
    
        missatge_preu=  "🔸*{}*\n[{}]({})\n{}\nBenzina 95 E5 = *{}*€\nDiesel A =  *{}*€.\n\n"\
                        "🔹*{}*\n[{}]({})\n{}\nBenzina 95 E5 = *{}*€\nDiesel A = *{}*€.\n\n"\
                        "🔸*{}*\n[{}]({})\n{}\nBenzina 95 E5 = *{}*€\nDiesel A = *{}*€.\n\n"\
                        "🔹*{}*\n[{}]({})\n{}\nBenzina 95 E5 = *{}*€\nDiesel A = *{}*€.".format(
                        (output_barates[0][1]),(output_barates[0][4]),(ubicacio),(output_barates[0][0]),(output_barates[0][2]),(output_barates[0][3]),\
                        (output_barates[1][1]),(output_barates[1][4]),(ubicacio1),(output_barates[1][0]),(output_barates[1][2]),(output_barates[1][3]),\
                        (output_barates[2][1]),(output_barates[2][4]),(ubicacio2),(output_barates[2][0]),(output_barates[2][2]),(output_barates[2][3]),\
                        (output_barates[3][1]),(output_barates[3][4]),(ubicacio3),(output_barates[3][0]),(output_barates[3][2]),(output_barates[3][3])
                        )
        query.edit_message_text(
        text= missatge_preu, parse_mode=telegram.ParseMode.MARKDOWN,
        reply_markup = InlineKeyboardMarkup([
            [button5]
            ])
        )
        return NIVELL1
    
def mes_cares(update, context= CallbackContext):
    output_cares = extractor_dades.estacions_servei_extraccio_benzina_descendent()
    try:
        adequacio_lat =  str.replace(output_cares[0][5], ',', '.')
        adequacio_long = str.replace(output_cares[0][6], ',', '.')
        adequacio_lat1 =  str.replace(output_cares[1][5], ',', '.')
        adequacio_long1 = str.replace(output_cares[1][6], ',', '.')
        adequacio_lat2 =  str.replace(output_cares[2][5], ',', '.')
        adequacio_long2 = str.replace(output_cares[2][6], ',', '.')
        adequacio_lat3 =  str.replace(output_cares[3][5], ',', '.')
        adequacio_long3 = str.replace(output_cares[3][6], ',', '.')
        adequacio_lat4 =  str.replace(output_cares[4][5], ',', '.')
        adequacio_long4 = str.replace(output_cares[4][6], ',', '.')
        ubicacio = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat, adequacio_long)
        ubicacio1 = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat1, adequacio_long1)
        ubicacio2 = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat2, adequacio_long2)
        ubicacio3 = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat3, adequacio_long3)
        ubicacio4 = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat4, adequacio_long4)
        query = update.callback_query
        query.answer()
        button5 = InlineKeyboardButton(
            b5, callback_data=str(PREU)
        )
    
        missatge_preu=  "🔸*{}*\n[{}]({})\n{}\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.\n\n"\
                        "🔹*{}*\n[{}]({})\n{}\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.\n\n"\
                        "🔸*{}*\n[{}]({})\n{}\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.\n\n"\
                        "🔹*{}*\n[{}]({})\n{}\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.\n\n"\
                        "🔸*{}*\n[{}]({})\n{}\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.".format(
                        (output_cares[0][1]),(output_cares[0][4]),(ubicacio),(output_cares[0][0]),(output_cares[0][2]),(output_cares[0][3]),\
                        (output_cares[1][1]),(output_cares[1][4]),(ubicacio1),(output_cares[1][0]),(output_cares[1][2]),(output_cares[1][3]),\
                        (output_cares[2][1]),(output_cares[2][4]),(ubicacio2),(output_cares[2][0]),(output_cares[2][2]),(output_cares[2][3]),\
                        (output_cares[3][1]),(output_cares[3][4]),(ubicacio3),(output_cares[3][0]),(output_cares[3][2]),(output_cares[3][3]),\
                        (output_cares[4][1]),(output_cares[4][4]),(ubicacio4),(output_cares[4][0]),(output_cares[4][2]),(output_cares[4][3])
                        )
        query.edit_message_text(
        text= missatge_preu, parse_mode=telegram.ParseMode.MARKDOWN,
        reply_markup = InlineKeyboardMarkup([
            [button5]
            ])
        )
        return NIVELL1
    except:
        adequacio_lat =  str.replace(output_cares[0][5], ',', '.')
        adequacio_long = str.replace(output_cares[0][6], ',', '.')
        adequacio_lat1 =  str.replace(output_cares[1][5], ',', '.')
        adequacio_long1 = str.replace(output_cares[1][6], ',', '.')
        adequacio_lat2 =  str.replace(output_cares[2][5], ',', '.')
        adequacio_long2 = str.replace(output_cares[2][6], ',', '.')
        adequacio_lat3 =  str.replace(output_cares[3][5], ',', '.')
        adequacio_long3 = str.replace(output_cares[3][6], ',', '.')
        ubicacio = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat, adequacio_long)
        ubicacio1 = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat1, adequacio_long1)
        ubicacio2 = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat2, adequacio_long2)
        ubicacio3 = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat3, adequacio_long3)
        query = update.callback_query
        query.answer()
        button5 = InlineKeyboardButton(
            b5, callback_data=str(PREU)
        )
    
        missatge_preu=  "🔸*{}*\n[{}]({})\n{}\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.\n\n"\
                        "🔹*{}*\n[{}]({})\n{}\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.\n\n"\
                        "🔸*{}*\n[{}]({})\n{}\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.\n\n"\
                        "🔹*{}*\n[{}]({})\n{}\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.".format(
                        (output_cares[0][1]),(output_cares[0][4]),(ubicacio),(output_cares[0][0]),(output_cares[0][2]),(output_cares[0][3]),\
                        (output_cares[1][1]),(output_cares[1][4]),(ubicacio1),(output_cares[1][0]),(output_cares[1][2]),(output_cares[1][3]),\
                        (output_cares[2][1]),(output_cares[2][4]),(ubicacio2),(output_cares[2][0]),(output_cares[2][2]),(output_cares[2][3]),\
                        (output_cares[3][1]),(output_cares[3][4]),(ubicacio3),(output_cares[3][0]),(output_cares[3][2]),(output_cares[3][3])
                        )
        query.edit_message_text(
        text= missatge_preu, parse_mode=telegram.ParseMode.MARKDOWN,
        reply_markup = InlineKeyboardMarkup([
            [button5]
            ])
        )
        return NIVELL1

def tipus_combustible(update, context= CallbackContext):
    query = update.callback_query
    query.answer()
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
    query.edit_message_text(
    text= missatge_preu, parse_mode=telegram.ParseMode.MARKDOWN,
    reply_markup = InlineKeyboardMarkup([
        [button8,button9],
        [button10,button11],
        [button12,button5]
        ])
    )
    return NIVELL2

def benzina(update, context= CallbackContext):
    output_benzina = extractor_dades.estacions_servei_extraccio_benzina_ascendent()
    try:
        query = update.callback_query
        query.answer()
        button5 = InlineKeyboardButton(
            b5, callback_data=str(COMBUSTIBLE)
        )
        missatge_preu = "🔸*{}*\n{}\n{}\nBenzina 95 E5 *{}*€.\n\n"\
                        "🔹*{}*\n{}\n{}\nBenzina 95 E5 *{}*€.\n\n"\
                        "🔸*{}*\n{}\n{}\nBenzina 95 E5 *{}*€.\n\n"\
                        "🔹*{}*\n{}\n{}\nBenzina 95 E5 *{}*€.\n\n"\
                        "🔸*{}*\n{}\n{}\nBenzina 95 E5 *{}*€.\n\n"\
                        "🔹*{}*\n{}\n{}\nBenzina 95 E5 *{}*€.\n\n"\
                        "🔸*{}*\n{}\n{}\nBenzina 95 E5 *{}*€.\n\n"\
                        "🔹*{}*\n{}\n{}\nBenzina 95 E5 *{}*€.\n\n"\
                        "🔸*{}*\n{}\n{}\nBenzina 95 E5 *{}*€.\n\n"\
                        "🔹*{}*\n{}\n{}\nBenzina 95 E5 *{}*€.\n\n"\
                        "🔸*{}*\n{}\n{}\nBenzina 95 E5 *{}*€.\n\n"\
                        "🔹*{}*\n{}\n{}\nBenzina 95 E5 *{}*€.\n\n"\
                        "🔸*{}*\n{}\n{}\nBenzina 95 E5 *{}*€.\n\n"\
                        "🔹*{}*\n{}\n{}\nBenzina 95 E5 *{}*€.\n\n"\
                        "🔸*{}*\n{}\n{}\nBenzina 95 E5 *{}*€.\n\n"\
                        "🔹*{}*\n{}\n{}\nBenzina 95 E5 *{}*€.\n\n"\
                        "🔸*{}*\n{}\n{}\nBenzina 95 E5 *{}*€.\n\n"\
                        "🔹*{}*\n{}\n{}\nBenzina 95 E5 *{}*€.\n\n"\
                        "🔸*{}*\n{}\n{}\nBenzina 95 E5 *{}*€.\n\n"\
                        "🔹*{}*\n{}\n{}\nBenzina 95 E5 *{}*€.\n\n"\
                        "🔸*{}*\n{}\n{}\nBenzina 95 E5 *{}*€.\n\n"\
                        "🔹*{}*\n{}\n{}\nBenzina 95 E5 *{}*€.".format(
                        (output_benzina[0][1]),(output_benzina[0][4]),(output_benzina[0][0]),(output_benzina[0][2]),
                        (output_benzina[1][1]),(output_benzina[1][4]),(output_benzina[1][0]),(output_benzina[1][2]),
                        (output_benzina[2][1]),(output_benzina[2][4]),(output_benzina[2][0]),(output_benzina[2][2]),
                        (output_benzina[3][1]),(output_benzina[3][4]),(output_benzina[3][0]),(output_benzina[3][2]),
                        (output_benzina[4][1]),(output_benzina[4][4]),(output_benzina[4][0]),(output_benzina[4][2]),
                        (output_benzina[5][1]),(output_benzina[5][4]),(output_benzina[5][0]),(output_benzina[5][2]),
                        (output_benzina[6][1]),(output_benzina[6][4]),(output_benzina[6][0]),(output_benzina[6][2]),
                        (output_benzina[7][1]),(output_benzina[7][4]),(output_benzina[7][0]),(output_benzina[7][2]),
                        (output_benzina[8][1]),(output_benzina[8][4]),(output_benzina[8][0]),(output_benzina[8][2]),
                        (output_benzina[9][1]),(output_benzina[9][4]),(output_benzina[9][0]),(output_benzina[9][2]),
                        (output_benzina[10][1]),(output_benzina[10][4]),(output_benzina[10][0]),(output_benzina[10][2]),
                        (output_benzina[11][1]),(output_benzina[11][4]),(output_benzina[11][0]),(output_benzina[11][2]),
                        (output_benzina[12][1]),(output_benzina[12][4]),(output_benzina[12][0]),(output_benzina[12][2]),
                        (output_benzina[13][1]),(output_benzina[13][4]),(output_benzina[13][0]),(output_benzina[13][2]),
                        (output_benzina[14][1]),(output_benzina[14][4]),(output_benzina[14][0]),(output_benzina[14][2]),
                        (output_benzina[15][1]),(output_benzina[15][4]),(output_benzina[15][0]),(output_benzina[15][2]),
                        (output_benzina[16][1]),(output_benzina[16][4]),(output_benzina[16][0]),(output_benzina[16][2]),
                        (output_benzina[17][1]),(output_benzina[17][4]),(output_benzina[17][0]),(output_benzina[17][2]),
                        (output_benzina[18][1]),(output_benzina[18][4]),(output_benzina[18][0]),(output_benzina[18][2]),
                        (output_benzina[19][1]),(output_benzina[19][4]),(output_benzina[19][0]),(output_benzina[19][2]),
                        (output_benzina[20][1]),(output_benzina[20][4]),(output_benzina[20][0]),(output_benzina[20][2]),
                        (output_benzina[21][1]),(output_benzina[21][4]),(output_benzina[21][0]),(output_benzina[21][2]),
                        )
        query.edit_message_text(
        text= missatge_preu, parse_mode=telegram.ParseMode.MARKDOWN,
        reply_markup = InlineKeyboardMarkup([
            [button5]
            ])
        )
        return NIVELL1
    except:
        query = update.callback_query
        query.answer()
        button5 = InlineKeyboardButton(
            b5, callback_data=str(COMBUSTIBLE)
        )
        missatge_preu = "🔸*{}*\n{}\n{}\nBenzina 95 E5 *{}*€.\n\n"\
                        "🔹*{}*\n{}\n{}\nBenzina 95 E5 *{}*€.\n\n"\
                        "🔸*{}*\n{}\n{}\nBenzina 95 E5 *{}*€.\n\n"\
                        "🔹*{}*\n{}\n{}\nBenzina 95 E5 *{}*€.\n\n"\
                        "🔸*{}*\n{}\n{}\nBenzina 95 E5 *{}*€.\n\n"\
                        "🔹*{}*\n{}\n{}\nBenzina 95 E5 *{}*€.\n\n"\
                        "🔸*{}*\n{}\n{}\nBenzina 95 E5 *{}*€.\n\n"\
                        "🔹*{}*\n{}\n{}\nBenzina 95 E5 *{}*€.\n\n"\
                        "🔸*{}*\n{}\n{}\nBenzina 95 E5 *{}*€.\n\n"\
                        "🔹*{}*\n{}\n{}\nBenzina 95 E5 *{}*€.\n\n"\
                        "🔸*{}*\n{}\n{}\nBenzina 95 E5 *{}*€.\n\n"\
                        "🔹*{}*\n{}\n{}\nBenzina 95 E5 *{}*€.\n\n"\
                        "🔸*{}*\n{}\n{}\nBenzina 95 E5 *{}*€.\n\n"\
                        "🔹*{}*\n{}\n{}\nBenzina 95 E5 *{}*€.\n\n"\
                        "🔸*{}*\n{}\n{}\nBenzina 95 E5 *{}*€.\n\n"\
                        "🔹*{}*\n{}\n{}\nBenzina 95 E5 *{}*€.\n\n"\
                        "🔸*{}*\n{}\n{}\nBenzina 95 E5 *{}*€.\n\n"\
                        "🔹*{}*\n{}\n{}\nBenzina 95 E5 *{}*€.\n\n"\
                        "🔸*{}*\n{}\n{}\nBenzina 95 E5 *{}*€.\n\n"\
                        "🔹*{}*\n{}\n{}\nBenzina 95 E5 *{}*€.\n\n"\
                        "🔸*{}*\n{}\n{}\nBenzina 95 E5 *{}*€.".format(
                        (output_benzina[0][1]),(output_benzina[0][4]),(output_benzina[0][0]),(output_benzina[0][2]),
                        (output_benzina[1][1]),(output_benzina[1][4]),(output_benzina[1][0]),(output_benzina[1][2]),
                        (output_benzina[2][1]),(output_benzina[2][4]),(output_benzina[2][0]),(output_benzina[2][2]),
                        (output_benzina[3][1]),(output_benzina[3][4]),(output_benzina[3][0]),(output_benzina[3][2]),
                        (output_benzina[4][1]),(output_benzina[4][4]),(output_benzina[4][0]),(output_benzina[4][2]),
                        (output_benzina[5][1]),(output_benzina[5][4]),(output_benzina[5][0]),(output_benzina[5][2]),
                        (output_benzina[6][1]),(output_benzina[6][4]),(output_benzina[6][0]),(output_benzina[6][2]),
                        (output_benzina[7][1]),(output_benzina[7][4]),(output_benzina[7][0]),(output_benzina[7][2]),
                        (output_benzina[8][1]),(output_benzina[8][4]),(output_benzina[8][0]),(output_benzina[8][2]),
                        (output_benzina[9][1]),(output_benzina[9][4]),(output_benzina[9][0]),(output_benzina[9][2]),
                        (output_benzina[10][1]),(output_benzina[10][4]),(output_benzina[10][0]),(output_benzina[10][2]),
                        (output_benzina[11][1]),(output_benzina[11][4]),(output_benzina[11][0]),(output_benzina[11][2]),
                        (output_benzina[12][1]),(output_benzina[12][4]),(output_benzina[12][0]),(output_benzina[12][2]),
                        (output_benzina[13][1]),(output_benzina[13][4]),(output_benzina[13][0]),(output_benzina[13][2]),
                        (output_benzina[14][1]),(output_benzina[14][4]),(output_benzina[14][0]),(output_benzina[14][2]),
                        (output_benzina[15][1]),(output_benzina[15][4]),(output_benzina[15][0]),(output_benzina[15][2]),
                        (output_benzina[16][1]),(output_benzina[16][4]),(output_benzina[16][0]),(output_benzina[16][2]),
                        (output_benzina[17][1]),(output_benzina[17][4]),(output_benzina[17][0]),(output_benzina[17][2]),
                        (output_benzina[18][1]),(output_benzina[18][4]),(output_benzina[18][0]),(output_benzina[18][2]),
                        (output_benzina[19][1]),(output_benzina[19][4]),(output_benzina[19][0]),(output_benzina[19][2]),
                        (output_benzina[20][1]),(output_benzina[20][4]),(output_benzina[20][0]),(output_benzina[20][2]),
                        )
        query.edit_message_text(
        text= missatge_preu, parse_mode=telegram.ParseMode.MARKDOWN,
        reply_markup = InlineKeyboardMarkup([
            [button5]
            ])
        )
        return NIVELL1

def gasoli_A(update, context= CallbackContext):
    output_gasoliA = extractor_dades.carburants_extraccio_diesel_A_ascendent()
    try:
        query = update.callback_query
        query.answer()
        button5 = InlineKeyboardButton(
            b5, callback_data=str(COMBUSTIBLE)
        )

        missatge_gasoliA=   "🔸*{}*\n{}\n{}\nGasoli A *{}*€.\n\n"\
                            "🔹*{}*\n{}\n{}\nGasoli A *{}*€.\n\n"\
                            "🔸*{}*\n{}\n{}\nGasoli A *{}*€.\n\n"\
                            "🔹*{}*\n{}\n{}\nGasoli A *{}*€.\n\n"\
                            "🔸*{}*\n{}\n{}\nGasoli A *{}*€.\n\n"\
                            "🔹*{}*\n{}\n{}\nGasoli A *{}*€.\n\n"\
                            "🔸*{}*\n{}\n{}\nGasoli A *{}*€.\n\n"\
                            "🔹*{}*\n{}\n{}\nGasoli A *{}*€.\n\n"\
                            "🔸*{}*\n{}\n{}\nGasoli A *{}*€.\n\n"\
                            "🔹*{}*\n{}\n{}\nGasoli A *{}*€.\n\n"\
                            "🔸*{}*\n{}\n{}\nGasoli A *{}*€.\n\n"\
                            "🔹*{}*\n{}\n{}\nGasoli A *{}*€.\n\n"\
                            "🔸*{}*\n{}\n{}\nGasoli A *{}*€.\n\n"\
                            "🔹*{}*\n{}\n{}\nGasoli A *{}*€.\n\n"\
                            "🔸*{}*\n{}\n{}\nGasoli A *{}*€.\n\n"\
                            "🔹*{}*\n{}\n{}\nGasoli A *{}*€.\n\n"\
                            "🔸*{}*\n{}\n{}\nGasoli A *{}*€.\n\n"\
                            "🔹*{}*\n{}\n{}\nGasoli A *{}*€.\n\n"\
                            "🔸*{}*\n{}\n{}\nGasoli A *{}*€.\n\n"\
                            "🔹*{}*\n{}\n{}\nGasoli A *{}*€.\n\n"\
                            "🔸*{}*\n{}\n{}\nGasoli A *{}*€.\n\n"\
                            "🔹*{}*\n{}\n{}\nGasoli A *{}*€.".format(
                            (output_gasoliA[0][1]),(output_gasoliA[0][3]),(output_gasoliA[0][0]),(output_gasoliA[0][2]),
                            (output_gasoliA[1][1]),(output_gasoliA[1][3]),(output_gasoliA[1][0]),(output_gasoliA[1][2]),
                            (output_gasoliA[2][1]),(output_gasoliA[2][3]),(output_gasoliA[2][0]),(output_gasoliA[2][2]),
                            (output_gasoliA[3][1]),(output_gasoliA[3][3]),(output_gasoliA[3][0]),(output_gasoliA[3][2]),
                            (output_gasoliA[4][1]),(output_gasoliA[4][3]),(output_gasoliA[4][0]),(output_gasoliA[4][2]),
                            (output_gasoliA[5][1]),(output_gasoliA[5][3]),(output_gasoliA[5][0]),(output_gasoliA[5][2]),
                            (output_gasoliA[6][1]),(output_gasoliA[6][3]),(output_gasoliA[6][0]),(output_gasoliA[6][2]),
                            (output_gasoliA[7][1]),(output_gasoliA[7][3]),(output_gasoliA[7][0]),(output_gasoliA[7][2]),
                            (output_gasoliA[8][1]),(output_gasoliA[8][3]),(output_gasoliA[8][0]),(output_gasoliA[8][2]),
                            (output_gasoliA[9][1]),(output_gasoliA[9][3]),(output_gasoliA[9][0]),(output_gasoliA[9][2]),
                            (output_gasoliA[10][1]),(output_gasoliA[10][3]),(output_gasoliA[10][0]),(output_gasoliA[10][2]),
                            (output_gasoliA[11][1]),(output_gasoliA[11][3]),(output_gasoliA[11][0]),(output_gasoliA[11][2]),
                            (output_gasoliA[12][1]),(output_gasoliA[12][3]),(output_gasoliA[12][0]),(output_gasoliA[12][2]),
                            (output_gasoliA[13][1]),(output_gasoliA[13][3]),(output_gasoliA[13][0]),(output_gasoliA[13][2]),
                            (output_gasoliA[14][1]),(output_gasoliA[14][3]),(output_gasoliA[14][0]),(output_gasoliA[14][2]),
                            (output_gasoliA[15][1]),(output_gasoliA[15][3]),(output_gasoliA[15][0]),(output_gasoliA[15][2]),
                            (output_gasoliA[16][1]),(output_gasoliA[16][3]),(output_gasoliA[16][0]),(output_gasoliA[16][2]),
                            (output_gasoliA[17][1]),(output_gasoliA[17][3]),(output_gasoliA[17][0]),(output_gasoliA[17][2]),
                            (output_gasoliA[18][1]),(output_gasoliA[18][3]),(output_gasoliA[18][0]),(output_gasoliA[18][2]),
                            (output_gasoliA[19][1]),(output_gasoliA[19][3]),(output_gasoliA[19][0]),(output_gasoliA[19][2]),
                            (output_gasoliA[20][1]),(output_gasoliA[20][3]),(output_gasoliA[20][0]),(output_gasoliA[20][2]),
                            (output_gasoliA[21][1]),(output_gasoliA[21][3]),(output_gasoliA[21][0]),(output_gasoliA[21][2])
                            )
        query.edit_message_text(
        text= missatge_gasoliA, parse_mode=telegram.ParseMode.MARKDOWN,
        reply_markup = InlineKeyboardMarkup([
            [button5]
            ])
        )
        return NIVELL1
    except:
        query = update.callback_query
        query.answer()
        button5 = InlineKeyboardButton(
            b5, callback_data=str(COMBUSTIBLE)
        )

        missatge_gasoliA=   "🔸*{}*\n{}\n{}\nGasoli A *{}*€.\n\n"\
                            "🔹*{}*\n{}\n{}\nGasoli A *{}*€.\n\n"\
                            "🔸*{}*\n{}\n{}\nGasoli A *{}*€.\n\n"\
                            "🔹*{}*\n{}\n{}\nGasoli A *{}*€.\n\n"\
                            "🔸*{}*\n{}\n{}\nGasoli A *{}*€.\n\n"\
                            "🔹*{}*\n{}\n{}\nGasoli A *{}*€.\n\n"\
                            "🔸*{}*\n{}\n{}\nGasoli A *{}*€.\n\n"\
                            "🔹*{}*\n{}\n{}\nGasoli A *{}*€.\n\n"\
                            "🔸*{}*\n{}\n{}\nGasoli A *{}*€.\n\n"\
                            "🔹*{}*\n{}\n{}\nGasoli A *{}*€.\n\n"\
                            "🔸*{}*\n{}\n{}\nGasoli A *{}*€.\n\n"\
                            "🔹*{}*\n{}\n{}\nGasoli A *{}*€.\n\n"\
                            "🔸*{}*\n{}\n{}\nGasoli A *{}*€.\n\n"\
                            "🔹*{}*\n{}\n{}\nGasoli A *{}*€.\n\n"\
                            "🔸*{}*\n{}\n{}\nGasoli A *{}*€.\n\n"\
                            "🔹*{}*\n{}\n{}\nGasoli A *{}*€.\n\n"\
                            "🔸*{}*\n{}\n{}\nGasoli A *{}*€.\n\n"\
                            "🔹*{}*\n{}\n{}\nGasoli A *{}*€.\n\n"\
                            "🔸*{}*\n{}\n{}\nGasoli A *{}*€.\n\n"\
                            "🔹*{}*\n{}\n{}\nGasoli A *{}*€.\n\n"\
                            "🔸*{}*\n{}\n{}\nGasoli A *{}*€.".format(
                            (output_gasoliA[0][1]),(output_gasoliA[0][3]),(output_gasoliA[0][0]),(output_gasoliA[0][2]),
                            (output_gasoliA[1][1]),(output_gasoliA[1][3]),(output_gasoliA[1][0]),(output_gasoliA[1][2]),
                            (output_gasoliA[2][1]),(output_gasoliA[2][3]),(output_gasoliA[2][0]),(output_gasoliA[2][2]),
                            (output_gasoliA[3][1]),(output_gasoliA[3][3]),(output_gasoliA[3][0]),(output_gasoliA[3][2]),
                            (output_gasoliA[4][1]),(output_gasoliA[4][3]),(output_gasoliA[4][0]),(output_gasoliA[4][2]),
                            (output_gasoliA[5][1]),(output_gasoliA[5][3]),(output_gasoliA[5][0]),(output_gasoliA[5][2]),
                            (output_gasoliA[6][1]),(output_gasoliA[6][3]),(output_gasoliA[6][0]),(output_gasoliA[6][2]),
                            (output_gasoliA[7][1]),(output_gasoliA[7][3]),(output_gasoliA[7][0]),(output_gasoliA[7][2]),
                            (output_gasoliA[8][1]),(output_gasoliA[8][3]),(output_gasoliA[8][0]),(output_gasoliA[8][2]),
                            (output_gasoliA[9][1]),(output_gasoliA[9][3]),(output_gasoliA[9][0]),(output_gasoliA[9][2]),
                            (output_gasoliA[10][1]),(output_gasoliA[10][3]),(output_gasoliA[10][0]),(output_gasoliA[10][2]),
                            (output_gasoliA[11][1]),(output_gasoliA[11][3]),(output_gasoliA[11][0]),(output_gasoliA[11][2]),
                            (output_gasoliA[12][1]),(output_gasoliA[12][3]),(output_gasoliA[12][0]),(output_gasoliA[12][2]),
                            (output_gasoliA[13][1]),(output_gasoliA[13][3]),(output_gasoliA[13][0]),(output_gasoliA[13][2]),
                            (output_gasoliA[14][1]),(output_gasoliA[14][3]),(output_gasoliA[14][0]),(output_gasoliA[14][2]),
                            (output_gasoliA[15][1]),(output_gasoliA[15][3]),(output_gasoliA[15][0]),(output_gasoliA[15][2]),
                            (output_gasoliA[16][1]),(output_gasoliA[16][3]),(output_gasoliA[16][0]),(output_gasoliA[16][2]),
                            (output_gasoliA[17][1]),(output_gasoliA[17][3]),(output_gasoliA[17][0]),(output_gasoliA[17][2]),
                            (output_gasoliA[18][1]),(output_gasoliA[18][3]),(output_gasoliA[18][0]),(output_gasoliA[18][2]),
                            (output_gasoliA[19][1]),(output_gasoliA[19][3]),(output_gasoliA[19][0]),(output_gasoliA[19][2]),
                            (output_gasoliA[20][1]),(output_gasoliA[20][3]),(output_gasoliA[20][0]),(output_gasoliA[20][2]),
                            )
        query.edit_message_text(
        text= missatge_gasoliA, parse_mode=telegram.ParseMode.MARKDOWN,
        reply_markup = InlineKeyboardMarkup([
            [button5]
            ])
        )
        return NIVELL1
def gasoli_B(update, context= CallbackContext):
    output_gasoliB = extractor_dades.carburants_extraccio_diesel_B_ascendent()
    try:
        query = update.callback_query
        query.answer()
        button5 = InlineKeyboardButton(
            b5, callback_data=str(COMBUSTIBLE)
        )
        missatge_gasoliB =  "🔸*{}*\n{}\n{}\nGasoli A *{}*€.\n\n"\
                            "🔹*{}*\n{}\n{}\nGasoli A *{}*€.".format(
                            (output_gasoliB[0][1]),(output_gasoliB[0][3]),(output_gasoliB[0][0]),(output_gasoliB[0][2]),
                            (output_gasoliB[1][1]),(output_gasoliB[1][3]),(output_gasoliB[1][0]),(output_gasoliB[1][2]),   
                            )
        query.edit_message_text(
        text= missatge_gasoliB, parse_mode=telegram.ParseMode.MARKDOWN,
        reply_markup = InlineKeyboardMarkup([
            [button5]
            ])
        )
        return NIVELL1
    except:
        query = update.callback_query
        query.answer()
        button5 = InlineKeyboardButton(
            b5, callback_data=str(COMBUSTIBLE)
        )
        missatge_gasoliB =  "🔹*{}*\n{}\n{}\nGasoli A *{}*€.".format(
                            (output_gasoliB[0][1]),(output_gasoliB[0][3]),(output_gasoliB[0][0]),(output_gasoliB[0][2]),  
                            )
        query.edit_message_text(
        text= missatge_gasoliB, parse_mode=telegram.ParseMode.MARKDOWN,
        reply_markup = InlineKeyboardMarkup([
            [button5]
            ])
        )
        return NIVELL1
def gasoli_Premium(update, context= CallbackContext):
    output_gasoliP = extractor_dades.carburants_extraccio_diesel_premium_ascendent()
    try:
        query = update.callback_query
        query.answer()
        button5 = InlineKeyboardButton(
            b5, callback_data=str(COMBUSTIBLE)
        )
        missatge_gasoliP =  "🔸*{}*\n{}\n{}\nGasoli Premium *{}*€.\n\n"\
                            "🔹*{}*\n{}\n{}\nGasoli Premium *{}*€.\n\n"\
                            "🔸*{}*\n{}\n{}\nGasoli Premium *{}*€.\n\n"\
                            "🔹*{}*\n{}\n{}\nGasoli Premium *{}*€.".format(
                            (output_gasoliP[0][1]),(output_gasoliP[0][3]),(output_gasoliP[0][0]),(output_gasoliP[0][2]),
                            (output_gasoliP[1][1]),(output_gasoliP[1][3]),(output_gasoliP[1][0]),(output_gasoliP[1][2]),
                            (output_gasoliP[2][1]),(output_gasoliP[2][3]),(output_gasoliP[1][0]),(output_gasoliP[2][2]),
                            (output_gasoliP[3][1]),(output_gasoliP[3][3]),(output_gasoliP[1][0]),(output_gasoliP[3][2]),   
                            )
        query.edit_message_text(
        text= missatge_gasoliP, parse_mode=telegram.ParseMode.MARKDOWN,
        reply_markup = InlineKeyboardMarkup([
            [button5]
            ])
        )
        return NIVELL1
    except:
        query = update.callback_query
        query.answer()
        button5 = InlineKeyboardButton(
            b5, callback_data=str(COMBUSTIBLE)
        )
        missatge_gasoliP =  "🔸*{}*\n{}\n{}\nGasoli Premium *{}*€.\n\n"\
                            "🔹*{}*\n{}\n{}\nGasoli Premium *{}*€.\n\n"\
                            "🔸*{}*\n{}\n{}\nGasoli Premium *{}*€.".format(
                            (output_gasoliP[0][1]),(output_gasoliP[0][3]),(output_gasoliP[0][0]),(output_gasoliP[0][2]),
                            (output_gasoliP[1][1]),(output_gasoliP[1][3]),(output_gasoliP[1][0]),(output_gasoliP[1][2]),
                            (output_gasoliP[2][1]),(output_gasoliP[2][3]),(output_gasoliP[1][0]),(output_gasoliP[2][2]),  
                            )
        query.edit_message_text(
        text= missatge_gasoliP, parse_mode=telegram.ParseMode.MARKDOWN,
        reply_markup = InlineKeyboardMarkup([
            [button5]
            ])
        )
        return NIVELL1
def GL_Petroli(update, context= CallbackContext):
    output_GLP = extractor_dades.carburants_extraccio_GLP_ascendent()
    try:
        query = update.callback_query
        query.answer()
        button5 = InlineKeyboardButton(
            b5, callback_data=str(COMBUSTIBLE)
        )
        missatge_GLP =  "🔸*{}*\n{}\n{}\nGLP *{}*€.\n\n"\
                        "🔹*{}*\n{}\n{}\nGLP *{}*€.".format(
                        (output_GLP[0][1]),(output_GLP[0][3]),(output_GLP[0][0]),(output_GLP[0][2]),
                        (output_GLP[1][1]),(output_GLP[1][3]),(output_GLP[1][0]),(output_GLP[1][2]),   
                            )
        query.edit_message_text(
        text= missatge_GLP, parse_mode=telegram.ParseMode.MARKDOWN,
        reply_markup = InlineKeyboardMarkup([
            [button5]
            ])
        )
        return NIVELL1
    except:
        query = update.callback_query
        query.answer()
        button5 = InlineKeyboardButton(
            b5, callback_data=str(COMBUSTIBLE)
        )
        missatge_GLP =  "🔹*{}*\n{}\n{}\nGLP *{}*€.".format(
                        (output_GLP[0][1]),(output_GLP[0][3]),(output_GLP[0][0]),(output_GLP[0][2]), 
                            )
        query.edit_message_text(
        text= missatge_GLP, parse_mode=telegram.ParseMode.MARKDOWN,
        reply_markup = InlineKeyboardMarkup([
            [button5]
            ])
        )
        return NIVELL1
def per_municipi(update, context= CallbackContext):
    query = update.callback_query
    query.answer()
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
    query.edit_message_text(
            text = m_instruct, parse_mode=telegram.ParseMode.MARKDOWN,
            reply_markup = InlineKeyboardMarkup([
                [button13, button14, button15],
                [button16, button17, button18],
                [button19, button20, button5]
            ])
        )
    return NIVELL2
def mao(update, context= CallbackContext):
    output_mao = extractor_dades.extraccio_MAO_ascendent()
    try:
        adequacio_lat =  str.replace(output_mao[0][5], ',', '.')
        adequacio_long = str.replace(output_mao[0][6], ',', '.')
        adequacio_lat1 =  str.replace(output_mao[1][5], ',', '.')
        adequacio_long1 = str.replace(output_mao[1][6], ',', '.')
        adequacio_lat2 =  str.replace(output_mao[2][5], ',', '.')
        adequacio_long2 = str.replace(output_mao[2][6], ',', '.')
        adequacio_lat3 =  str.replace(output_mao[3][5], ',', '.')
        adequacio_long3 = str.replace(output_mao[3][6], ',', '.')
        adequacio_lat4 =  str.replace(output_mao[4][5], ',', '.')
        adequacio_long4 = str.replace(output_mao[4][6], ',', '.')
        adequacio_lat5 =  str.replace(output_mao[5][5], ',', '.')
        adequacio_long5 = str.replace(output_mao[5][6], ',', '.')
        adequacio_lat6 =  str.replace(output_mao[6][5], ',', '.')
        adequacio_long6 = str.replace(output_mao[6][6], ',', '.')
        ubicacio = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat, adequacio_long)
        ubicacio1 = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat1, adequacio_long1)
        ubicacio2 = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat2, adequacio_long2)
        ubicacio3 = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat3, adequacio_long3)
        ubicacio4 = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat4, adequacio_long4)
        ubicacio5 = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat5, adequacio_long5)
        ubicacio6 = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat6, adequacio_long6)
        query = update.callback_query
        query.answer()
        button5 = InlineKeyboardButton(
            b5, callback_data=str(POBLE)
        )
        missatge_mao =  "🔸*{}*\n[{}]({})\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.\n\n"\
                        "🔹*{}*\n[{}]({})\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.\n\n"\
                        "🔸*{}*\n[{}]({})\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.\n\n"\
                        "🔹*{}*\n[{}]({})\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.\n\n"\
                        "🔸*{}*\n[{}]({})\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.\n\n"\
                        "🔹*{}*\n[{}]({})\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.\n\n"\
                        "🔸*{}*\n[{}]({})\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.".format(
                            (output_mao[0][1]),(output_mao[0][4]),(ubicacio),(output_mao[0][2]),(output_mao[0][3]),
                            (output_mao[1][1]),(output_mao[1][4]),(ubicacio1),(output_mao[1][2]),(output_mao[1][3]),
                            (output_mao[2][1]),(output_mao[2][4]),(ubicacio2),(output_mao[2][2]),(output_mao[2][3]),
                            (output_mao[3][1]),(output_mao[3][4]),(ubicacio3),(output_mao[3][2]),(output_mao[3][3]),
                            (output_mao[4][1]),(output_mao[4][4]),(ubicacio4),(output_mao[4][2]),(output_mao[4][3]),
                            (output_mao[5][1]),(output_mao[5][4]),(ubicacio5),(output_mao[5][2]),(output_mao[5][3]),
                            (output_mao[6][1]),(output_mao[6][4]),(ubicacio6),(output_mao[6][2]),(output_mao[6][3]),
                        )
        query.edit_message_text(
                text = missatge_mao, parse_mode=telegram.ParseMode.MARKDOWN,
                reply_markup = InlineKeyboardMarkup([
                    [button5]
                ])
            )
        return NIVELL1
    except:
        adequacio_lat =  str.replace(output_mao[0][5], ',', '.')
        adequacio_long = str.replace(output_mao[0][6], ',', '.')
        adequacio_lat1 =  str.replace(output_mao[1][5], ',', '.')
        adequacio_long1 = str.replace(output_mao[1][6], ',', '.')
        adequacio_lat2 =  str.replace(output_mao[2][5], ',', '.')
        adequacio_long2 = str.replace(output_mao[2][6], ',', '.')
        adequacio_lat3 =  str.replace(output_mao[3][5], ',', '.')
        adequacio_long3 = str.replace(output_mao[3][6], ',', '.')
        adequacio_lat4 =  str.replace(output_mao[4][5], ',', '.')
        adequacio_long4 = str.replace(output_mao[4][6], ',', '.')
        adequacio_lat5 =  str.replace(output_mao[5][5], ',', '.')
        adequacio_long5 = str.replace(output_mao[5][6], ',', '.')
        ubicacio = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat, adequacio_long)
        ubicacio1 = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat1, adequacio_long1)
        ubicacio2 = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat2, adequacio_long2)
        ubicacio3 = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat3, adequacio_long3)
        ubicacio4 = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat4, adequacio_long4)
        ubicacio5 = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat5, adequacio_long5)
        query = update.callback_query
        query.answer()
        button5 = InlineKeyboardButton(
            b5, callback_data=str(POBLE)
        )
        missatge_mao =  "🔸*{}*\n[{}]({})\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.\n\n"\
                        "🔹*{}*\n[{}]({})\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.\n\n"\
                        "🔸*{}*\n[{}]({})\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.\n\n"\
                        "🔹*{}*\n[{}]({})\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.\n\n"\
                        "🔸*{}*\n[{}]({})\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.\n\n"\
                        "🔹*{}*\n[{}]({})\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.".format(
                            (output_mao[0][1]),(output_mao[0][4]),(ubicacio),(output_mao[0][2]),(output_mao[0][3]),
                            (output_mao[1][1]),(output_mao[1][4]),(ubicacio1),(output_mao[1][2]),(output_mao[1][3]),
                            (output_mao[2][1]),(output_mao[2][4]),(ubicacio2),(output_mao[2][2]),(output_mao[2][3]),
                            (output_mao[3][1]),(output_mao[3][4]),(ubicacio3),(output_mao[3][2]),(output_mao[3][3]),
                            (output_mao[4][1]),(output_mao[4][4]),(ubicacio4),(output_mao[4][2]),(output_mao[4][3]),
                            (output_mao[5][1]),(output_mao[5][4]),(ubicacio5),(output_mao[5][2]),(output_mao[5][3]),
                        )
        query.edit_message_text(
                text = missatge_mao, parse_mode=telegram.ParseMode.MARKDOWN,
                reply_markup = InlineKeyboardMarkup([
                    [button5]
                ])
            )
        return NIVELL1
def ciutadella(update, context= CallbackContext):
    output_ciutadella = extractor_dades.extraccio_CIUTADELLA_ascendent()
    try:
        adequacio_lat =  str.replace(output_ciutadella[0][5], ',', '.')
        adequacio_long = str.replace(output_ciutadella[0][6], ',', '.')
        adequacio_lat1 =  str.replace(output_ciutadella[1][5], ',', '.')
        adequacio_long1 = str.replace(output_ciutadella[1][6], ',', '.')
        adequacio_lat2 =  str.replace(output_ciutadella[2][5], ',', '.')
        adequacio_long2 = str.replace(output_ciutadella[2][6], ',', '.')
        adequacio_lat3 =  str.replace(output_ciutadella[3][5], ',', '.')
        adequacio_long3 = str.replace(output_ciutadella[3][6], ',', '.')
        adequacio_lat4 =  str.replace(output_ciutadella[4][5], ',', '.')
        adequacio_long4 = str.replace(output_ciutadella[4][6], ',', '.')
        ubicacio = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat, adequacio_long)
        ubicacio1 = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat1, adequacio_long1)
        ubicacio2 = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat2, adequacio_long2)
        ubicacio3 = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat3, adequacio_long3)
        ubicacio4 = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat4, adequacio_long4)
        query = update.callback_query
        query.answer()
        button5 = InlineKeyboardButton(
            b5, callback_data=str(POBLE)
        )
        missatge_ciutadella =   "🔸*{}*\n[{}]({})\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.\n\n"\
                                "🔹*{}*\n[{}]({})\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.\n\n"\
                                "🔸*{}*\n[{}]({})\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.\n\n"\
                                "🔹*{}*\n[{}]({})\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.\n\n"\
                                "🔸*{}*\n[{}]({})\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.".format(
                                    (output_ciutadella[0][1]),(output_ciutadella[0][4]),(ubicacio),(output_ciutadella[0][2]),(output_ciutadella[0][3]),
                                    (output_ciutadella[1][1]),(output_ciutadella[1][4]),(ubicacio1),(output_ciutadella[1][2]),(output_ciutadella[1][3]),
                                    (output_ciutadella[2][1]),(output_ciutadella[2][4]),(ubicacio2),(output_ciutadella[2][2]),(output_ciutadella[2][3]),
                                    (output_ciutadella[3][1]),(output_ciutadella[3][4]),(ubicacio3),(output_ciutadella[3][2]),(output_ciutadella[3][3]),
                                    (output_ciutadella[4][1]),(output_ciutadella[4][4]),(ubicacio4),(output_ciutadella[4][2]),(output_ciutadella[4][3])
                        )
        query.edit_message_text(
                text = missatge_ciutadella, parse_mode=telegram.ParseMode.MARKDOWN,
                reply_markup = InlineKeyboardMarkup([
                    [button5]
                ])
            )
        return NIVELL1
    except:
        adequacio_lat =  str.replace(output_ciutadella[0][5], ',', '.')
        adequacio_long = str.replace(output_ciutadella[0][6], ',', '.')
        adequacio_lat1 =  str.replace(output_ciutadella[1][5], ',', '.')
        adequacio_long1 = str.replace(output_ciutadella[1][6], ',', '.')
        adequacio_lat2 =  str.replace(output_ciutadella[2][5], ',', '.')
        adequacio_long2 = str.replace(output_ciutadella[2][6], ',', '.')
        adequacio_lat3 =  str.replace(output_ciutadella[3][5], ',', '.')
        adequacio_long3 = str.replace(output_ciutadella[3][6], ',', '.')
        ubicacio = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat, adequacio_long)
        ubicacio1 = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat1, adequacio_long1)
        ubicacio2 = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat2, adequacio_long2)
        ubicacio3 = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat3, adequacio_long3)
        query = update.callback_query
        query.answer()
        button5 = InlineKeyboardButton(
            b5, callback_data=str(POBLE)
        )
        missatge_ciutadella =   "🔸*{}*\n[{}]({})\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.\n\n"\
                                "🔹*{}*\n[{}]({})\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.\n\n"\
                                "🔸*{}*\n[{}]({})\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.\n\n"\
                                "🔹*{}*\n[{}]({})\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.".format(
                                    (output_ciutadella[0][1]),(output_ciutadella[0][4]),(ubicacio),(output_ciutadella[0][2]),(output_ciutadella[0][3]),
                                    (output_ciutadella[1][1]),(output_ciutadella[1][4]),(ubicacio1),(output_ciutadella[1][2]),(output_ciutadella[1][3]),
                                    (output_ciutadella[2][1]),(output_ciutadella[2][4]),(ubicacio2),(output_ciutadella[2][2]),(output_ciutadella[2][3]),
                                    (output_ciutadella[3][1]),(output_ciutadella[3][4]),(ubicacio3),(output_ciutadella[3][2]),(output_ciutadella[3][3])
                        )
        query.edit_message_text(
                text = missatge_ciutadella, parse_mode=telegram.ParseMode.MARKDOWN,
                reply_markup = InlineKeyboardMarkup([
                    [button5]
                ])
            )
        return NIVELL1

def alaior(update, context= CallbackContext):
    output_alaior = extractor_dades.extraccio_ALAIOR_ascendent()
    try:
        adequacio_lat =  str.replace(output_alaior[0][5], ',', '.')
        adequacio_long = str.replace(output_alaior[0][6], ',', '.')
        adequacio_lat1 =  str.replace(output_alaior[1][5], ',', '.')
        adequacio_long1 = str.replace(output_alaior[1][6], ',', '.')
        adequacio_lat2 =  str.replace(output_alaior[2][5], ',', '.')
        adequacio_long2 = str.replace(output_alaior[2][6], ',', '.')
        ubicacio = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat, adequacio_long)
        ubicacio1 = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat1, adequacio_long1)
        ubicacio2 = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat2, adequacio_long2)
        query = update.callback_query
        query.answer()
        button5 = InlineKeyboardButton(
            b5, callback_data=str(POBLE)
        )
        missatge_alaior =   "🔸*{}*\n[{}]({})\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.\n\n"\
                            "🔹*{}*\n[{}]({})\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.\n\n"\
                            "🔸*{}*\n[{}]({})\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.".format(
                                (output_alaior[0][1]),(output_alaior[0][4]),(ubicacio),(output_alaior[0][2]),(output_alaior[0][3]),
                                (output_alaior[1][1]),(output_alaior[1][4]),(ubicacio1),(output_alaior[1][2]),(output_alaior[1][3]),
                                (output_alaior[2][1]),(output_alaior[2][4]),(ubicacio2),(output_alaior[2][2]),(output_alaior[2][3]),
                        )
        query.edit_message_text(
                text = missatge_alaior, parse_mode=telegram.ParseMode.MARKDOWN,
                reply_markup = InlineKeyboardMarkup([
                    [button5]
                ])
            )
        return NIVELL1
    except:
        adequacio_lat =  str.replace(output_alaior[0][5], ',', '.')
        adequacio_long = str.replace(output_alaior[0][6], ',', '.')
        adequacio_lat1 =  str.replace(output_alaior[1][5], ',', '.')
        adequacio_long1 = str.replace(output_alaior[1][6], ',', '.')
        ubicacio = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat, adequacio_long)
        ubicacio1 = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat1, adequacio_long1)
        query = update.callback_query
        query.answer()
        button5 = InlineKeyboardButton(
            b5, callback_data=str(POBLE)
        )
        missatge_alaior =   "🔸*{}*\n[{}]({})\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.\n\n"\
                            "🔹*{}*\n[{}]({})\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.".format(
                                (output_alaior[0][1]),(output_alaior[0][4]),(ubicacio),(output_alaior[0][2]),(output_alaior[0][3]),
                                (output_alaior[1][1]),(output_alaior[1][4]),(ubicacio1),(output_alaior[1][2]),(output_alaior[1][3]),
                        )
        query.edit_message_text(
                text = missatge_alaior, parse_mode=telegram.ParseMode.MARKDOWN,
                reply_markup = InlineKeyboardMarkup([
                    [button5]
                ])
            )
        return NIVELL1
def ferreries(update, context= CallbackContext):
    output_ferreries = extractor_dades.extraccio_FERRERIES_ascendent()
    try:
        adequacio_lat =  str.replace(output_ferreries[0][5], ',', '.')
        adequacio_long = str.replace(output_ferreries[0][6], ',', '.')
        ubicacio = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat, adequacio_long)
        query = update.callback_query
        query.answer()
        button5 = InlineKeyboardButton(
            b5, callback_data=str(POBLE)
        )
        missatge_ferreries =   "🔸*{}*\n[{}]({})\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.".format(
                                (output_ferreries[0][1]),(output_ferreries[0][4]),(ubicacio),(output_ferreries[0][2]),(output_ferreries[0][3]),

                        )
        query.edit_message_text(
                text = missatge_ferreries, parse_mode=telegram.ParseMode.MARKDOWN,
                reply_markup = InlineKeyboardMarkup([
                    [button5]
                ])
            )
        return NIVELL1
    except:
        query = update.callback_query
        query.answer()
        button5 = InlineKeyboardButton(
            b5, callback_data=str(POBLE)
        )
        missatge_ferreries =    "😨❌No disponible en aquests moments "

        query.edit_message_text(
                text = missatge_ferreries, parse_mode=telegram.ParseMode.MARKDOWN,
                reply_markup = InlineKeyboardMarkup([
                    [button5]
                ])
            )
        return NIVELL1    
def mercadal(update, context= CallbackContext):
    output_merdal = extractor_dades.extraccio_MERDAL_ascendent()
    try:
        adequacio_lat =  str.replace(output_merdal[0][5], ',', '.')
        adequacio_long = str.replace(output_merdal[0][6], ',', '.')
        adequacio_lat1 =  str.replace(output_merdal[1][5], ',', '.')
        adequacio_long1 = str.replace(output_merdal[1][6], ',', '.')
        ubicacio = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat, adequacio_long)
        ubicacio1 = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat1, adequacio_long1)
        query = update.callback_query
        query.answer()
        button5 = InlineKeyboardButton(
            b5, callback_data=str(POBLE)
        )
        missatge_merdal =   "🔹*{}*\n[{}]({})\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.\n\n"\
                            "🔸*{}*\n[{}]({})\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.".format(
                                (output_merdal[0][1]),(output_merdal[0][4]),(ubicacio),(output_merdal[0][2]),(output_merdal[0][3]),
                                (output_merdal[1][1]),(output_merdal[1][4]),(ubicacio1),(output_merdal[1][2]),(output_merdal[1][3])
                        )
        query.edit_message_text(
                text = missatge_merdal, parse_mode=telegram.ParseMode.MARKDOWN,
                reply_markup = InlineKeyboardMarkup([
                    [button5]
                ])
            )
        return NIVELL1
    except:
        adequacio_lat =  str.replace(output_merdal[0][5], ',', '.')
        adequacio_long = str.replace(output_merdal[0][6], ',', '.')
        ubicacio = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat, adequacio_long)
        query = update.callback_query
        query.answer()
        button5 = InlineKeyboardButton(
            b5, callback_data=str(POBLE)
        )
        missatge_merdal =   "🔸*{}*\n[{}]({})\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.".format(
                            (output_merdal[0][1]),(output_merdal[0][4]),(ubicacio),(output_merdal[0][2]),(output_merdal[0][3]),
                        )
        query.edit_message_text(
                text = missatge_merdal, parse_mode=telegram.ParseMode.MARKDOWN,
                reply_markup = InlineKeyboardMarkup([
                    [button5]
                ])
            )
        return NIVELL1
def santlluis(update, context= CallbackContext):
    output_santlluis = extractor_dades.extraccio_SANTLLUIS_ascendent()
    try:
        adequacio_lat =  str.replace(output_santlluis[0][5], ',', '.')
        adequacio_long = str.replace(output_santlluis[0][6], ',', '.')
        adequacio_lat1 =  str.replace(output_santlluis[1][5], ',', '.')
        adequacio_long1 = str.replace(output_santlluis[1][6], ',', '.')
        ubicacio = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat, adequacio_long)
        ubicacio1 = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat1, adequacio_long1)
        query = update.callback_query
        query.answer()
        button5 = InlineKeyboardButton(
            b5, callback_data=str(POBLE)
        )
        missatge_santlluis =    "🔹*{}*\n[{}]({})\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.\n\n"\
                                "🔸*{}*\n[{}]({})\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.".format(
                                    (output_santlluis[0][1]),(output_santlluis[0][4]),(ubicacio),(output_santlluis[0][2]),(output_santlluis[0][3]),
                                    (output_santlluis[1][1]),(output_santlluis[1][4]),(ubicacio1),(output_santlluis[1][2]),(output_santlluis[1][3])
                        )
        query.edit_message_text(
                text = missatge_santlluis, parse_mode=telegram.ParseMode.MARKDOWN,
                reply_markup = InlineKeyboardMarkup([
                    [button5]
                ])
            )
        return NIVELL1
    except:
        adequacio_lat =  str.replace(output_santlluis[0][5], ',', '.')
        adequacio_long = str.replace(output_santlluis[0][6], ',', '.')
        ubicacio = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat, adequacio_long)

        query = update.callback_query
        query.answer()
        button5 = InlineKeyboardButton(
            b5, callback_data=str(POBLE)
        )
        missatge_santlluis =    "🔸*{}*\n[{}]({})\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.".format(
                                    (output_santlluis[0][1]),(output_santlluis[0][4]),(ubicacio),(output_santlluis[0][2]),(output_santlluis[0][3]),
                           )
        query.edit_message_text(
                text = missatge_santlluis, parse_mode=telegram.ParseMode.MARKDOWN,
                reply_markup = InlineKeyboardMarkup([
                    [button5]
                ])
            )
        return NIVELL1
def fornells(update, context= CallbackContext):
    output_fornells = extractor_dades.extraccio_FORNELLS_ascendent()
    try:
        adequacio_lat =  39.9787575 #str.replace(output_fornells[0][4], ',', '.')
        adequacio_long = 4.194645 #str.replace(output_fornells[0][5], ',', '.')
        ubicacio = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat, adequacio_long)
        query = update.callback_query
        query.answer()
        button5 = InlineKeyboardButton(
            b5, callback_data=str(POBLE)
        )
        missatge_fornells =   "🔸*{}*\n[{}]({})\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.".format(
                                (output_fornells[0][0]),(output_fornells[0][1]),(ubicacio),(output_fornells[0][2]),(output_fornells[0][3]),

                        )
        query.edit_message_text(
                text = missatge_fornells, parse_mode=telegram.ParseMode.MARKDOWN,
                reply_markup = InlineKeyboardMarkup([
                    [button5]
                ])
            )
        return NIVELL1
    except:
        query = update.callback_query
        query.answer()
        button5 = InlineKeyboardButton(
            b5, callback_data=str(POBLE)
        )
        missatge_fornells =    "😨❌No disponible en aquests moments"

        query.edit_message_text(
                text = missatge_fornells, parse_mode=telegram.ParseMode.MARKDOWN,
                reply_markup = InlineKeyboardMarkup([
                    [button5]
                ])
            )
        return NIVELL1    
def escastell(update, context= CallbackContext):
    output_escastell = extractor_dades.extraccio_ESCASTELL_ascendent()
    try:
        adequacio_lat =  str.replace(output_escastell[0][5], ',', '.')
        adequacio_long = str.replace(output_escastell[0][6], ',', '.')
        ubicacio = 'https://www.google.com/maps/@{},{},20z'.format(adequacio_lat, adequacio_long)
        query = update.callback_query
        query.answer()
        button5 = InlineKeyboardButton(
            b5, callback_data=str(POBLE)
        )
        missatge_ferreries =   "🔸*{}*\n[{}]({})\nBenzina 95 E5 *{}*€\nDiesel A *{}*€.".format(
                                (output_escastell[0][1]),(output_escastell[0][4]),(ubicacio),(output_escastell[0][2]),(output_escastell[0][3]),

                        )
        query.edit_message_text(
                text = missatge_ferreries, parse_mode=telegram.ParseMode.MARKDOWN,
                reply_markup = InlineKeyboardMarkup([
                    [button5]
                ])
            )
        return NIVELL1
    except:
        query = update.callback_query
        query.answer()
        button5 = InlineKeyboardButton(
            b5, callback_data=str(POBLE)
            )
        missatge_ferreries =   "😨❌No disponible en aquests moments"
                        
        query.edit_message_text(
                text = missatge_ferreries, parse_mode=telegram.ParseMode.MARKDOWN,
                reply_markup = InlineKeyboardMarkup([
                    [button5]
                ])
            )
        return NIVELL1


def info(update, context= CallbackContext):
    query = update.callback_query
    query.answer()
    button5 = InlineKeyboardButton(
        b5, callback_data=str(INICI)
    )
    missatge_info = "Dades extretes de *Ministerio de Industria, Comercio y Turismo*.\n"\
                    "S'ha comprobat que algunes dades d'ubicació están malament o no son prou precises.\n"\
                    "Ses dades errónees han estat notificades.\n\n"\
                    "*Última actualització de preus:* {}\n\n"\
                    "Escrit per Damia Sintes.\nCodi a [GitHub](https://github.com/Damiasroca/Bot_Menorca_EESS)".format((last_update.last()))
    query.edit_message_text(
            text = missatge_info, parse_mode=telegram.ParseMode.MARKDOWN,
            reply_markup = InlineKeyboardMarkup([
                [button5]
            ])
        )
    return NIVELL1
    







def main():

    persistencia = PicklePersistence(filename='persistencia_arxiu')
    updater = Updater(secret.secret["bot_token"], persistence = persistencia, use_context=True)

    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NIVELL0:[
                CallbackQueryHandler(start_over, pattern=str(INICI))
            ],
            NIVELL1:[
                CallbackQueryHandler(preu, pattern= str(PREU)),
                CallbackQueryHandler(tipus_combustible, pattern= str(COMBUSTIBLE)),
                CallbackQueryHandler(per_municipi, pattern= str(POBLE)),
                CallbackQueryHandler(info, pattern= str(INFO)),
                CallbackQueryHandler(start_over, pattern=str(INICI))
            ],
            NIVELL2:[
                CallbackQueryHandler(mes_barates, pattern= str(BARATES)),
                CallbackQueryHandler(mes_cares, pattern= str(CARES)),
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
    dp.add_handler(conv_handler)

    dp.add_handler(CommandHandler('start', start))

    
    
 
  

    updater.start_polling()
    updater.idle()

main()