import os
import asyncio
import requests
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# 🔐 Variables de entorno
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Pon tu token real aquí
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # Pon tu chat ID aquí

# Fichas iniciales
fichas = 1500  # equivalentes a 1500 MXN

# Función para obtener datos de Binance
def obtener_datos_binance():
    try:
        data = requests.get("https://api.binance.com/api/v3/ticker/24hr").json()
        if not isinstance(data, list):
            print("Binance API no devolvió lista, ignorando.")
            return []
    except Exception as e:
        print("Error Binance:", e)
        return []

    oportunidades = []
    for m in data[:5]:  # solo los primeros 5 para prueba
        try:
            precio_cambio = float(m.get("priceChangePercent", 0))
            volumen = float(m.get("volume", 0))
            if volumen > 1000 and precio_cambio > 2:
                oportunidades.append(m)
        except Exception as e:
            print("Error parseando mercado Binance:", e)
            continue
    return oportunidades

# Función para obtener datos de Polymarket (simulación)
def obtener_datos_polymarket():
    return [{"pregunta": "¿Bitcoin > 50k en 2 semanas?", "probabilidad": 0.55}]

# Función de ciclo de inversión
async def ciclo(bot: Bot):
    global fichas
    while True:
        oportunidades = []

        # Binance
        oportunidades += obtener_datos_binance()
        # Polymarket
        oportunidades += obtener_datos_polymarket()

        if oportunidades:
            msg = f"Oportunidades encontradas: {len(oportunidades)}\n"
            for op in oportunidades:
                msg += str(op) + "\n"
            try:
                await bot.send_message(chat_id=CHAT_ID, text=msg)
            except Exception as e:
                print("Error enviando mensaje:", e)

        # Esperar 30 minutos antes del siguiente ciclo
        await asyncio.sleep(1800)

# Handlers de Telegram
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot activo 🚀")

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.lower()
    if "hola" in texto:
        await update.message.reply_text("¡Hola! ¿Cómo estás?")
    elif "qué tal" in texto:
        await update.message.reply_text("Todo va bien 😎, revisando los mercados.")

# Función principal
async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Comandos
    app.add_handler(CommandHandler("start", start))
    # Mensajes de texto
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), responder))

    # Iniciar ciclo de inversión
    bot = Bot(TOKEN)
    asyncio.create_task(ciclo(bot))

    # Ejecutar bot
    await app.run_polling()

# Ejecutar main
if __name__ == "__main__":
    asyncio.run(main())
