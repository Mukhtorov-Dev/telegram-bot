from datetime import datetime, timedelta

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, Filters)

from conf import TOKEN, DB_NAME
from db_helper import DBHelper

BTN_TODAY, BTN_TOMORROW, BTN_MONTH, BTN_REGION, BTN_DUA = (
    '⌛️ Bugungi taqvim', '⏳ Ertangi taqvim', "📅 To'liq taqvim", "🇺🇿 Viloyatni o'zgartirish", '🤲 Duo')
main_buttons = ReplyKeyboardMarkup([
    [BTN_TODAY], [BTN_TOMORROW, BTN_MONTH], [BTN_REGION], [BTN_DUA]
], resize_keyboard=True)

STATE_REGION = 1
STATE_CALENDAR = 2

user_region = dict()
db = DBHelper(DB_NAME)


def region_buttons():
    regions = db.get_regions()
    buttons = []
    tmp_b = []
    for region in regions:
        tmp_b.append(InlineKeyboardButton(region['name'], callback_data=region['id']))
        if len(tmp_b) == 2:
            buttons.append(tmp_b)
            tmp_b = []
    return buttons


def start(update, context):
    user = update.message.from_user
    user_region[user.id] = None
    buttons = region_buttons()

    update.message.reply_html(
        "Assalomu alaykum <b>{}!</b>\n \n<b>Ramazon oyi muborak bo'lsin</b>\n \nSizga qaysi viloyat taqvimi kerak?".
            format(user.first_name), reply_markup=InlineKeyboardMarkup(buttons))

    return STATE_REGION


def inline_callback(update, context):
    try:
        query = update.callback_query
        user_id = query.from_user.id
        user_region[user_id] = int(query.data)
        query.message.delete()
        query.message.reply_html(text='<b>Ramazon taqvim</b> 2⃣0⃣2⃣1⃣ \n\n<b>XИЖРИЙ 1️⃣4️⃣4️⃣2️⃣-ЙИЛ</b>\n \nQuyidagilardan birini tanlang 👇',
                                 reply_markup=main_buttons)

        return STATE_CALENDAR
    except Exception as e:
        print('error ', str(e))


def calendar_today(update, context):
    try:
        user_id = update.message.from_user.id
        if not user_region[user_id]:
            return STATE_REGION
        region_id = user_region[user_id]
        region = db.get_region(region_id)
        today = str(datetime.now().date())

        calendar = db.get_calendar_by_region(region_id, today)

        update.message.reply_html('<b>Ramazon</b> 2021 \n<b>XИЖРИЙ</b> 1442-ЙИЛ \n\n<b>{}</b> vaqti:\n \nSaxarlik: <b>{}</b>\nIftorlik: <b>{}</b>'.format(
            region['name'], calendar['fajr'][:5], calendar['maghrib'][:5]))


    except Exception as e:
        print('Error ', str(e))

def calendar_tomorrow(update, context):
    try:
        user_id = update.message.from_user.id
        if not user_region[user_id]:
            return STATE_REGION
        region_id = user_region[user_id]
        region = db.get_region(region_id)
        dt = str(datetime.now().date() + timedelta(days=1))

        calendar = db.get_calendar_by_region(region_id, dt)

        update.message.reply_html('<b>Ramazon</b> 2021 \n<b>XИЖРИЙ</b> 1442-ЙИЛ  ️\n\n<b>{}</b> vaqti:\n \nSaxarlik: <b>{}</b>\nIftorlik: <b>{}</b>'.format(
            region['name'], calendar['fajr'][:5], calendar['maghrib'][:5]))


    except Exception as e:
        print('Error ', str(e))


def calendar_month(update, context):
    try:
        user_id = update.message.from_user.id
        if not user_region[user_id]:
            return STATE_REGION
        region_id = user_region[user_id]
        region = db.get_region(region_id)

        photo_path = 'images/table/region_{}.jpg'.format(region['id'])
        message = "<b>Ramazon</b> 2021 \n<b>XИЖРИЙ</b> 1442-ЙИЛ\n\n<b>{}</b>  <b>vaqti</b>".format(region['name'])

        update.message.reply_photo(photo=open(photo_path, 'rb'), caption=message, parse_mode='HTML',
                                   reply_markup=main_buttons)
    except Exception as e:
        print('Error ', str(e))


def select_region(update, context):
    buttons = region_buttons()
    update.message.reply_text("Sizga qaysi viloyat bo'yicha ko'rsatay?",
                              reply_markup=InlineKeyboardMarkup(buttons))
    return STATE_REGION


def select_dua(update, context):
    saharlik = "<b>Саҳарлик (оғиз ёпиш) дуоси:</b>\nНавайту ан асума совма шаҳри Рамазона минал фажри илал мағриби, холисан лиллаҳи таъала."
    iftorlik = "<b>Ифторлик (оғиз очиш) дуоси:</b>\nАллоҳумма лака сумту ва бика аманту ва аъалайка таваккалту ва ъала ризқика афтарту, фағфирли, йа Ғоффару, ма қоддамту вама аххорту."
    update.message.reply_photo(photo=open('images/ramadan_dua.png', 'rb'),
                               caption="{}\n \n{}".format(saharlik, iftorlik), parse_mode='HTML',
                               reply_markup=main_buttons)


def main():
    # Updater o`rnatib olamiz
    updater = Updater(TOKEN, use_context=True)

    # Dispatcher eventlarni aniqlash uchun
    dispatcher = updater.dispatcher

    # start kommandasini ushlab qolish
    # dispatcher.add_handler(CommandHandler('start', start))

    # inline button query
    # dispatcher.add_handler(CallbackQueryHandler(inline_callback))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            STATE_REGION: [
                CallbackQueryHandler(inline_callback),
                MessageHandler(Filters.regex('^(' + BTN_TODAY + ')$'), calendar_today),
                MessageHandler(Filters.regex('^(' + BTN_TOMORROW + ')$'), calendar_tomorrow),
                MessageHandler(Filters.regex('^(' + BTN_MONTH + ')$'), calendar_month),
                MessageHandler(Filters.regex('^(' + BTN_REGION + ')$'), select_region),
                MessageHandler(Filters.regex('^(' + BTN_DUA + ')$'), select_dua)

            ],
            STATE_CALENDAR: [
                MessageHandler(Filters.regex('^(' + BTN_TODAY + ')$'), calendar_today),
                MessageHandler(Filters.regex('^(' + BTN_TOMORROW + ')$'), calendar_tomorrow),
                MessageHandler(Filters.regex('^(' + BTN_MONTH + ')$'), calendar_month),
                MessageHandler(Filters.regex('^(' + BTN_REGION + ')$'), select_region),
                MessageHandler(Filters.regex('^(' + BTN_DUA + ')$'), select_dua)
            ],
        },
        fallbacks=[CommandHandler('start', start)]
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


main()