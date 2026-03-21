import os
import asyncio
import requests
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# 🔐 Variables de entorno
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # tu token aquí
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # tu chat ID aquí

fichas = 1500  # Inicial

def obtener_datos_binance():
    try:
        data = requests.get("https://api.binance.com/api/v3/ticker/24hr").json()
        if not isinstance(data, list):
            return []
    except Exception as e:
        print("Error Binance:", e)
        return []

    oportunidades = []
    for m in data[:5]:
        try:
            precio_cambio = float(m.get("priceChangePercent", 0))
            volumen = float(m.get("volume", 0))
            if volumen > 1000 and precio_cambio > 2:
                oportunidades.append(m)
        except Exception as e:
            continue
    return oportunidades

def obtener_datos_polymarket():
    return [{"pregunta": "¿Bitcoin > 50k en 2 semanas?", "probabilidad": 0.55}]

async def ciclo(bot: Bot):
    global fichas
    while True:
        oportunidades = []
        oportunidades += obtener_datos_binance()
        oportunidades += obtener_datos_polymarket()

        if oportunidades:
            msg = f"Oportunidades encontradas: {len(oportunidades)}\n"
            for op in oportunidades:
                msg += str(op) + "\n"
            try:
                await bot.send_message(chat_id=CHAT_ID, text=msg)
            except Exception as e:
                print("Error enviando mensaje:", e)

        await asyncio.sleep(1800)  # 30 min

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot activo 🚀")

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.lower()
    if "hola" in texto:
        await update.message.reply_text("¡Hola! ¿Cómo estás?")
    elif "qué tal" in texto:
        await update.message.reply_text("Todo va bien 😎, revisando los mercados.")

async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), responder))

    bot = Bot(TOKEN)
    asyncio.create_task(ciclo(bot))

    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
