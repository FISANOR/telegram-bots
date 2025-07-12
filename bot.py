import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer

def run_dummy_server():
    server_address = ("0.0.0.0", 10000)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    httpd.serve_forever()

threading.Thread(target=run_dummy_server).start()

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes

# Этапы анкеты
FIO, ADDRESS, PHONE, BIRTHDATE, ORDER = range(5)

# Твои данные
OWNER_ID = 5410641725
TOKEN = "7538776202:AAG0LuTPTDIe-6D_q5GhINlF3J3Dzucgczc"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я приму ваш заказ. Сначала, пожалуйста, введите ваше Ф.И.О.:")
    return FIO

async def get_fio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["fio"] = update.message.text
    await update.message.reply_text("Место, где вы живёте:")
    return ADDRESS

async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["address"] = update.message.text
    await update.message.reply_text("Ваш номер телефона:")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    await update.message.reply_text("Дата рождения (дд.мм.гггг):")
    return BIRTHDATE

async def get_birthdate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["birthdate"] = update.message.text
    await update.message.reply_text("Какие товары вы хотите заказать?\nНапишите всё в одном сообщении:")
    return ORDER

async def get_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["order"] = update.message.text

    data = context.user_data
    msg = f"""📦 Новый заказ от клиента:

👤 Ф.И.О.: {data['fio']}
🏠 Адрес: {data['address']}
📞 Телефон: {data['phone']}
🎂 Дата рождения: {data['birthdate']}
🛒 Заказ: {data['order']}
"""

    await context.bot.send_message(chat_id=OWNER_ID, text=msg)
    await update.message.reply_text("✅ Спасибо! Ваш заказ принят. Мы скоро с вами свяжемся.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Заказ отменён.")
    return ConversationHandler.END

# Создание приложения и регистрация хендлеров
app = ApplicationBuilder().token(TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        FIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_fio)],
        ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_address)],
        PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
        BIRTHDATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_birthdate)],
        ORDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_order)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

app.add_handler(conv_handler)

print("🤖 Бот запущен и принимает заказы...")
app.run_polling()
