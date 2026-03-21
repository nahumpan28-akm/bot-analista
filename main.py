import asyncio
import requests
import json
import os
from telegram import Bot

# 🔐 Variables de entorno (SEGURIDAD)
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Validación básica (evita errores silenciosos)
if not TOKEN or not CHAT_ID:
    raise ValueError("Faltan variables de entorno TOKEN o CHAT_ID")

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

# 📡 Obtener datos filtrados de Polymarket
def obtener_datos():
    url = "https://gamma-api.polymarket.com/markets"
    
    try:
        data = requests.get(url).json()
    except Exception as e:
        print("Error al obtener datos:", e)
        return []

    mercados_validos = []

    for m in data:
        try:
            if m.get("active") and not m.get("closed"):
                volumen = float(m.get("volume", 0))

                if volumen > 1000:
                    mercados_validos.append(m)
        except:
            continue

    return mercados_validos[:3]

# 🔁 Ciclo automático
async def ciclo():
    print("Bot activo en servidor 🚀")

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
Volumen: {int(volumen)}

{decision}
"""

                await bot.send_message(
                    chat_id=CHAT_ID,
                    text=mensaje
                )

            except Exception as e:
                print("Error en mercado:", e)

        await asyncio.sleep(300)  # cada 5 minutos

# ▶️ Ejecutar
if __name__ == "__main__":
    asyncio.run(ciclo())
