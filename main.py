from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = "8666785234:AAH5ECWNv3pJYmFVQ449CsSq58Yzy-tRWdI"

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = update.message.text.lower()

    if "hola" in mensaje:
        respuesta = "Hola Fidel 👋"
    elif "up" in mensaje:
        respuesta = "📈 Señal: UP"
    elif "down" in mensaje:
        respuesta = "📉 Señal: DOWN"
    else:
        respuesta = "No entendí eso 🤖"

    await update.message.reply_text(respuesta)

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

print("Bot activo en servidor 🚀")

app.run_polling()
