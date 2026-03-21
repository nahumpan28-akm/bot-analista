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
    # Solo operaciones con probabilidad alta y volumen decente
    if volumen < 1000 or probabilidad < 0.8:
        return False  # no invertir
    return True

# 🧠 IA básica para Binance
def evaluar_binance(precio_actual, tendencia_14dias):
    # Solo invertir si la tendencia indica subida clara
    if tendencia_14dias < 0.05:  # menos del 5% de subida en 14 días → ignorar
        return False
    return True

# 📡 Obtener datos Polymarket
def obtener_datos_polymarket():
    try:
        url = "https://gamma-api.polymarket.com/markets"
        data = requests.get(url).json()
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
        except:
            continue
    return mercados_validos[:3]

# 📡 Obtener datos Binance (simplificación: solo precio + tendencia 14 días)
def obtener_datos_binance():
    try:
        url = "https://api.binance.com/api/v3/ticker/24hr"
        data = requests.get(url).json()
    except Exception as e:
        print("Error Binance:", e)
        return []

    mercados_validos = []
    for m in data[:5]:  # solo los primeros 5 para prueba
        try:
            precio = float(m.get("lastPrice", 0))
            # tendencia 14 días simulada: porcentaje cambio de precio
            cambio = float(m.get("priceChangePercent", 0)) / 100
            if evaluar_binance(precio, cambio):
                mercados_validos.append({
                    "tipo": "Binance",
                    "nombre": m.get("symbol"),
                    "precio": precio,
                    "tendencia": cambio
                })
        except:
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
            mensaje += f"{op['tipo']}: {op['nombre']} → +{inversion} fichas\n"

        if oportunidades:
            try:
                await bot.send_message(chat_id=CHAT_ID, text=mensaje)
            except Exception as e:
                print("Error al enviar mensaje:", e)

        await asyncio.sleep(300)  # cada 5 minutos

# ▶️ Ejecutar
if __name__ == "__main__":
    asyncio.run(ciclo())
