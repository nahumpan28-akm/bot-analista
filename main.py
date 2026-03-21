import asyncio
import requests
import json
import os
from datetime import datetime
from telegram import Bot

# 🔐 Variables de entorno
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not TOKEN or not CHAT_ID:
    raise ValueError("Faltan variables de entorno TOKEN o CHAT_ID")

bot = Bot(token=TOKEN)

# 💰 Fichas iniciales
fichas = 1500
historial = []  # Guardará cada operación

# 🧠 IA básica para Polymarket
def evaluar_polymarket(probabilidad, volumen):
    if volumen < 1000 or probabilidad < 0.8:
        return False  # no invertir
    return True

# 🧠 IA básica para Binance
def evaluar_binance(precio_actual, tendencia_14dias):
    if tendencia_14dias < 0.05:  # menos del 5% de subida → ignorar
        return False
    return True

# 📡 Obtener datos Polymarket
def obtener_datos_polymarket():
    try:
        url = "https://gamma-api.polymarket.com/markets"
        data = requests.get(url, timeout=10).json()
    except Exception as e:
        print("Error Polymarket:", e)
        return []

    mercados_validos = []
    for m in data:
        try:
            if m.get("active") and not m.get("closed"):
                volumen = float(m.get("volume", 0))
                prices_raw = m.get("outcomePrices", "[]")
                prices = json.loads(prices_raw)
                if len(prices) == 0:
                    continue
                prob = float(prices[0])
                if evaluar_polymarket(prob, volumen):
                    mercados_validos.append({
                        "tipo": "Polymarket",
                        "nombre": m.get("question", "Sin nombre"),
                        "prob": prob,
                        "volumen": volumen
                    })
        except Exception as e:
            print("Error procesando mercado Polymarket:", e)
            continue
    return mercados_validos[:3]

# 📡 Obtener datos Binance
def obtener_datos_binance():
    try:
        url = "https://api.binance.com/api/v3/ticker/24hr"
        response = requests.get(url, timeout=10)
        data = response.json()
    except Exception as e:
        print("Error Binance:", e)
        return []

    if not isinstance(data, list):
        print("Binance retornó datos inesperados:", data)
        return []

    mercados_validos = []
    for m in data[:5]:  # solo los primeros 5 para prueba
        try:
            precio = float(m.get("lastPrice", 0))
            cambio = float(m.get("priceChangePercent", 0)) / 100
            if evaluar_binance(precio, cambio):
                mercados_validos.append({
                    "tipo": "Binance",
                    "nombre": m.get("symbol"),
                    "precio": precio,
                    "tendencia": cambio
                })
        except Exception as e:
            print("Error procesando mercado Binance:", e)
            continue
    return mercados_validos

# 🔁 Ciclo automático
async def ciclo():
    global fichas
    print("Bot activo en servidor 🚀")
    while True:
        oportunidades = []

        # Polymarket
        oportunidades += obtener_datos_polymarket()
        # Binance
        oportunidades += obtener_datos_binance()

        mensaje = f"📊 Reporte de operaciones {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nFichas: {fichas}\n\n"

        for op in oportunidades:
            # Simulación: invertir 50 fichas en cada oportunidad segura
            inversion = 50
            fichas += inversion  # Como nunca puede perder, sumamos (simulación)
            historial.append({
                "fecha": datetime.now().isoformat(),
                "tipo": op["tipo"],
                "nombre": op["nombre"],
                "inversion": inversion
            })
            if op["tipo"] == "Polymarket":
                mensaje += f"{op['tipo']}: {op['nombre']} → Prob: {op['prob']:.2f}, Volumen: {int(op['volumen'])} → +{inversion} fichas\n"
            else:
                mensaje += f"{op['tipo']}: {op['nombre']} → Precio: {op['precio']}, Tendencia: {op['tendencia']*100:.2f}% → +{inversion} fichas\n"

        if oportunidades:
            try:
                await bot.send_message(chat_id=CHAT_ID, text=mensaje)
            except Exception as e:
                print("Error al enviar mensaje:", e)

        await asyncio.sleep(300)  # cada 5 minutos

# ▶️ Ejecutar
if __name__ == "__main__":
    asyncio.run(ciclo())
