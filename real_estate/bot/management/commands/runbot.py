from django.core.management import BaseCommand
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler, \
    Application
from django.conf import settings
from bot.models import UserInfo
from asgiref.sync import sync_to_async

PHONE_NUMBER, NAME, OPTION = range(3)


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
    user_info = UserInfo(
        phone_number=context.user_data['phone_number'],
        name=context.user_data['name'],
        option='sell' if update.message.text == 'Продати квартиру' else 'rent'
    )
    await sync_to_async(user_info.save)()
    await update.message.reply_text('Ваші дані збережено!')
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
            },
            fallbacks=[CommandHandler('cancel', cancel)],
        )

        application.add_handler(conv_handler)

        application.run_polling(allowed_updates=Update.ALL_TYPES)
        # updater.idle()
