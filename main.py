import asyncio
import requests
import json
import os
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# 🔐 Variables de entorno
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not TOKEN or not CHAT_ID:
    raise ValueError("Faltan variables de entorno TOKEN o CHAT_ID")

bot = Bot(token=TOKEN)

# IA básica
def evaluar_trade(probabilidad, volumen):
    if volumen < 1000:
        return "❌ IGNORAR"
    if probabilidad > 0.75:
        return "📈 BUENA (UP)"
    elif probabilidad < 0.25:
        return "📉 BUENA (DOWN)"
    elif 0.40 < probabilidad < 0.60:
        return "⚠️ BASURA"
    else:
        return "🤔 DUDOSO"

# Datos Polymarket
def obtener_datos_polymarket():
    try:
        data = requests.get("https://gamma-api.polymarket.com/markets").json()
    except:
        return []
    mercados_validos = []
    for m in data:
        try:
            if m.get("active") and not m.get("closed") and float(m.get("volume", 0)) > 1000:
                mercados_validos.append(m)
        except:
            continue
    return mercados_validos[:3]

# Datos Binance
def obtener_datos_binance():
    try:
        data = requests.get("https://api.binance.com/api/v3/ticker/24hr").json()
    except:
        return []
    oportunidades = []
    for m in data[:5]:
        try:
            precio_cambio = float(m.get("priceChangePercent", 0))
            volumen = float(m.get("volume", 0))
            if volumen > 1000 and precio_cambio > 2:
                oportunidades.append(m)
        except:
            continue
    return oportunidades

# Responder mensajes simples
async def responder_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.lower()
    if "hola" in texto:
        await update.message.reply_text("¡Hola! ¿Cómo estás?")
    elif "qué tal" in texto or "como van las cosas" in texto:
        await update.message.reply_text("Todo va bien 🚀, revisando mercados!")

# Ciclo automático
async def ciclo():
    print("Bot activo en servidor 🚀")
    while True:
        oportunidades = []
        oportunidades += obtener_datos_polymarket()
        oportunidades += obtener_datos_binance()

        for mercado in oportunidades:
            try:
                if "question" in mercado:  # Polymarket
                    pregunta = mercado.get("question", "Sin nombre")
                    prices_raw = mercado.get("outcomePrices", "[]")
                    prices = json.loads(prices_raw)
                    if len(prices) == 0:
                        continue
                    prob = float(prices[0])
                    volumen = float(mercado.get("volume", 0))
                else:  # Binance
                    pregunta = mercado.get("symbol", "Sin nombre")
                    prob = float(mercado.get("priceChangePercent", 0)) / 100
                    volumen = float(mercado.get("volume", 0))

                decision = evaluar_trade(prob, volumen)
                mensaje = f"""
📊 {pregunta}

Probabilidad: {prob:.2f}
Volumen: {int(volumen)}

{decision}
"""
                await bot.send_message(chat_id=CHAT_ID, text=mensaje)
            except Exception as e:
                print("Error en mercado:", e)

        await asyncio.sleep(300)  # cada 5 minutos

# Configurar y ejecutar bot
async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder_mensaje))

    # Crear tarea del ciclo dentro del mismo loop de telegram
    asyncio.create_task(ciclo())

    # Iniciar el polling (gestiona su propio loop)
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
