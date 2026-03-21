import os
import asyncio
import requests
from telegram import Bot
from datetime import datetime

# -----------------------
# CONFIGURACIÓN DEL BOT
# -----------------------
TOKEN = os.getenv("TELEGRAM_TOKEN")  # tu token como variable de entorno
CHAT_ID_ENV = os.getenv("TELEGRAM_CHAT_ID")
if TOKEN is None or CHAT_ID_ENV is None:
    raise Exception("Debes definir TELEGRAM_TOKEN y TELEGRAM_CHAT_ID en las variables de entorno")
CHAT_ID = int(CHAT_ID_ENV)
bot = Bot(token=TOKEN)

# -----------------------
# CAPITAL INICIAL
# -----------------------
capital = 1500  # MXN en fichas
capital_minimo = 1000
capital_actual = capital

# -----------------------
# ARCHIVOS
# -----------------------
FILENAME = "historial.txt"

# -----------------------
# FUNCIONES DE SIMULACIÓN DE TRADING
# -----------------------
async def obtener_datos_binance():
    """Obtiene datos de Binance (solo precios actuales de BTC/USDT)"""
    try:
        response = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT")
        data = response.json()
        precio = float(data['price'])
        return precio
    except:
        return None

async def obtener_datos_polymarket():
    """Simulación de datos de Polymarket"""
    import random
    return random.uniform(0.3, 0.7)  # probabilidad de un evento

def decidir_operacion(precio_binance, prob_polymarket):
    """Decide si comprar, vender o no hacer nada"""
    import random
    decision = None
    riesgo = random.choice(["muy bajo", "bajo", "medio", "alto"])
    if riesgo == "muy bajo" and prob_polymarket > 0.55:
        decision = "comprar"
    elif riesgo == "bajo" and prob_polymarket > 0.6:
        decision = "comprar"
    elif riesgo == "medio" and prob_polymarket > 0.65:
        decision = "comprar"
    elif riesgo == "alto" and prob_polymarket > 0.7:
        decision = "comprar"
    else:
        decision = "vender"
    return decision, riesgo

def ejecutar_operacion(decision, riesgo):
    """Simula la operación y actualiza el capital"""
    global capital_actual
    import random
    factor = {"muy bajo": 0.01, "bajo": 0.03, "medio": 0.07, "alto": 0.15}
    if decision == "comprar":
        ganancia = capital_actual * factor[riesgo] * random.uniform(0.8, 1.2)
        capital_actual += ganancia
    else:
        perdida = capital_actual * factor[riesgo] * random.uniform(0.8, 1.2)
        capital_actual -= perdida
    if capital_actual < capital_minimo:
        return False  # desactivar bot
    return True

# -----------------------
# FUNCIONES DE REPORTE
# -----------------------
async def enviar_reporte(mensaje_extra=""):
    """Envía un reporte al chat de Telegram"""
    global capital_actual
    mensaje = f"Reporte de Bot:\nCapital actual: {capital_actual:.2f} fichas.\n{mensaje_extra}"
    await bot.send_message(chat_id=CHAT_ID, text=mensaje)
    with open(FILENAME, "a") as f:
        f.write(f"{datetime.now()} - {mensaje}\n")

# -----------------------
# HANDLER DE MENSAJES
# -----------------------
async def revisar_mensajes():
    """Revisa mensajes y responde a saludos"""
    global capital_actual
    offset = None
    while True:
        try:
            updates = await bot.get_updates(offset=offset, timeout=10)
            for update in updates:
                offset = update.update_id + 1
                if update.message:
                    texto = update.message.text.lower()
                    if "hola" in texto or "que tal" in texto:
                        await enviar_reporte("¡Hola! Aquí está tu reporte solicitado.")
        except Exception as e:
            print("Error revisando mensajes:", e)
        await asyncio.sleep(5)

# -----------------------
# LOOP PRINCIPAL
# -----------------------
async def main():
    global capital_actual
    contador_reporte = 0
    while True:
        precio_binance = await obtener_datos_binance()
        prob_polymarket = await obtener_datos_polymarket()
        decision, riesgo = decidir_operacion(precio_binance, prob_polymarket)
        activo = ejecutar_operacion(decision, riesgo)
        if not activo:
            await enviar_reporte("Capital muy bajo. Bot desactivado.")
            break
        contador_reporte += 1
        if contador_reporte >= 5:  # cada 5 iteraciones ~5 min
            await enviar_reporte(f"Operación reciente: {decision} con riesgo {riesgo}.")
            contador_reporte = 0
        await asyncio.sleep(60)  # espera 1 min por iteración

# -----------------------
# EJECUCIÓN CONCURRENTE
# -----------------------
async def correr_bot():
    await asyncio.gather(
        main(),
        revisar_mensajes()
    )

if __name__ == "__main__":
    asyncio.run(correr_bot())
