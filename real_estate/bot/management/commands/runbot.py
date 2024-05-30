from django.core.management import BaseCommand
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler, \
    Application
from django.conf import settings
from bot.models import UserInfo
from asgiref.sync import sync_to_async

PHONE_NUMBER, NAME, OPTION, PRICE, LOCATION, SUMMARY = range(6)


async def start(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text('Введіть ваш номер телефону:')
    return PHONE_NUMBER


async def phone_number(update: Update, context: CallbackContext) -> int:
    context.user_data['phone_number'] = update.message.text
    await update.message.reply_text('Введіть ваше ім’я:')
    return NAME


async def name(update: Update, context: CallbackContext) -> int:
    context.user_data['name'] = update.message.text
    options = [['Продати квартиру', 'Здати квартиру']]
    reply_markup = ReplyKeyboardMarkup(options, one_time_keyboard=True)
    await update.message.reply_text('Оберіть варіант:', reply_markup=reply_markup)
    return OPTION


async def option(update: Update, context: CallbackContext) -> int:
    context.user_data['option'] = update.message.text
    await update.message.reply_text('Введіть ціну:')
    return PRICE


async def price(update: Update, context: CallbackContext) -> int:
    context.user_data['price'] = update.message.text
    await update.message.reply_text('Введіть локацію:')
    return LOCATION


async def location(update: Update, context: CallbackContext) -> int:
    context.user_data['location'] = update.message.text
    await update.message.reply_text('Ваші дані збережено!')
    options = [['Показати дані', ]]
    reply_markup = ReplyKeyboardMarkup(options, one_time_keyboard=True)
    await update.message.reply_text('Оберіть дію:', reply_markup=reply_markup)
    return SUMMARY


async def summary(update: Update, context: CallbackContext) -> int:
    phone = context.user_data['phone_number']
    name = context.user_data['name']
    option = context.user_data["option"]
    price = context.user_data["price"]
    location = context.user_data["location"]
    await update.message.reply_text(f"Номер телефону - {phone},\n"
                                    f"Імя - {name},\n"
                                    f"Опція - {option},\n"
                                    f"Ціна - {price},\n"
                                    f"Локація - {location}")
    return ConversationHandler.END


async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text('Введення скасовано.')
    return ConversationHandler.END


class Command(BaseCommand):
    help = 'Run the Telegram bot'

    def handle(self, *args, **options):
        print("Bot started")
        application = Application.builder().token(settings.TELEGRAM_API_KEY).build()
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],
            states={
                PHONE_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone_number)],
                NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
                OPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, option)],
                PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, price)],
                LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, location)],
                SUMMARY: [MessageHandler(filters.TEXT & ~filters.COMMAND, summary)]
            },
            fallbacks=[CommandHandler('cancel', cancel)],
        )

        application.add_handler(conv_handler)

        application.run_polling(allowed_updates=Update.ALL_TYPES)
