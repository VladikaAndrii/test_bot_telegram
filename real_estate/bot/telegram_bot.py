from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler, \
    Application
from django.conf import settings
from .models import UserInfo

PHONE_NUMBER, NAME, OPTION = range(3)


async def start(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text('Введіть ваш номер телефону:')
    return PHONE_NUMBER


def phone_number(update: Update, context: CallbackContext) -> int:
    context.user_data['phone_number'] = update.message.text
    update.message.reply_text('Введіть ваше ім’я:')
    return NAME


def name(update: Update, context: CallbackContext) -> int:
    context.user_data['name'] = update.message.text
    options = [['Продати квартиру', 'Здати квартиру']]
    reply_markup = ReplyKeyboardMarkup(options, one_time_keyboard=True)
    update.message.reply_text('Оберіть варіант:', reply_markup=reply_markup)
    return OPTION


def option(update: Update, context: CallbackContext) -> int:
    user_info = UserInfo(
        phone_number=context.user_data['phone_number'],
        name=context.user_data['name'],
        option='sell' if update.message.text == 'Продати квартиру' else 'rent'
    )
    user_info.save()
    update.message.reply_text('Ваші дані збережено!')
    return ConversationHandler.END


async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text('Введення скасовано.')
    return ConversationHandler.END


def main() -> None:
    application = Application.builder().token(settings.TELEGRAM_API_KEY).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            PHONE_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, PHONE_NUMBER)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, NAME)],
            OPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, OPTION)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)
    # updater.idle()
