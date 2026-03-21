import asyncio
import requests
from telegram import Bot

TOKEN = "8666785234:AAH5ECWNv3pJYmFVQ449CsSq58Yzy-tRWdI"
CHAT_ID = "8236390565"

bot = Bot(token=TOKEN)

# 🧠 IA básica
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

# 📡 Obtener datos reales
def obtener_datos():
    url = "https://gamma-api.polymarket.com/markets"
    data = requests.get(url).json()
    return data[:3]  # solo 3 mercados para probar

# 🔁 Ciclo automático
async def ciclo():
    while True:
        mercados = obtener_datos()

        for mercado in mercados:
            try:
                pregunta = mercado["question"]
                prob = float(mercado["outcomes"][0]["price"])
                volumen = float(mercado["volume"])

                decision = evaluar_trade(prob, volumen)

                mensaje = f"""
📊 {pregunta}

Probabilidad: {prob}
Volumen: {volumen}

{decision}
"""

                await bot.send_message(chat_id=CHAT_ID, text=mensaje)

            except Exception as e:
                print("Error en mercado:", e)

        await asyncio.sleep(300)  # cada 5 minutos

# ▶️ Ejecutar
asyncio.run(ciclo())
