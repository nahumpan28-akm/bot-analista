import asyncio
import requests
import json
from telegram import Bot

TOKEN = "8666785234:AAH_MifjgyY2IB5OM8htFR_MSU7_OZAewms"
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
    response = requests.get(url)
    return response.json()[:3]

# 🔁 Ciclo automático
async def ciclo():
    while True:
        mercados = obtener_datos()

        for mercado in mercados:
            try:
                pregunta = mercado.get("question", "Sin nombre")

                prices_raw = mercado.get("outcomePrices", "[]")
                prices = json.loads(prices_raw)

                if len(prices) == 0:
                    continue

                prob = float(prices[0])
                volumen = float(mercado.get("volume", 0))

                decision = evaluar_trade(prob, volumen)

                mensaje = f"""
📊 {pregunta}

Probabilidad: {prob:.2f}
Volumen: {volumen}

{decision}
"""

                await bot.send_message(chat_id=CHAT_ID, text=mensaje)

            except Exception as e:
                print("Error en mercado:", e)

        await asyncio.sleep(300)  # cada 5 minutos

# ▶️ Ejecutar
asyncio.run(ciclo())
