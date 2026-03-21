import os
import asyncio
import requests
from datetime import datetime
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# -----------------------
# CONFIGURACIÓN DEL BOT
# -----------------------
TOKEN = os.getenv("TELEGRAM_TOKEN")
if TOKEN is None:
    raise Exception("Debes definir TELEGRAM_TOKEN en las variables de entorno")

CHAT_ID_ENV = os.getenv("TELEGRAM_CHAT_ID")
if CHAT_ID_ENV is None:
    raise Exception("Debes definir TELEGRAM_CHAT_ID en las variables de entorno")
CHAT_ID = int(CHAT_ID_ENV)

# -----------------------
# CAPITAL INICIAL
# -----------------------
capital = 1500  # MXN en fichas
capital_minimo = 1000
capital_actual = capital

# -----------------------
# ARCHIVO DE HISTORIAL
# -----------------------
FILENAME = "historial.txt"

# -----------------------
# FUNCIONES DE TRADING
# -----------------------
async def obtener_datos_binance():
    try:
        response = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT")
        data = response.json()
        return float(data['price'])
    except:
        return None

async def obtener_datos_polymarket():
    return random.uniform(0.3, 0.8)

def decidir_operacion(prob_polymarket):
    riesgo = random.choice(["muy bajo", "bajo", "medio", "alto"])
    decision = None
    if riesgo == "muy bajo" and prob_polymarket > 0.55:
        decision = "comprar"
    elif riesgo == "bajo" and prob_polymarket > 0.6:
        decision = "comprar"
    elif riesgo == "medio" and prob_polymarket > 0.65:
        decision = "comprar"
    elif riesgo == "alto" and prob_polymarket > 0.75:
        decision = "comprar"
    else:
        decision = "vender"
    return decision, riesgo

def ejecutar_operacion(decision, riesgo):
    global capital_actual
    factor = {"muy bajo": 0.02, "bajo": 0.04, "medio": 0.07, "alto": 0.12}
    cantidad = capital_actual * factor[riesgo]
    ganancia_perdida = cantidad * random.uniform(0.9, 1.1)
    capital_antes = capital_actual

    if decision == "comprar":
        capital_actual += ganancia_perdida
        resultado = f"Ganó {ganancia_perdida:.2f} fichas"
    else:
        capital_actual -= ganancia_perdida
        resultado = f"Perdió {ganancia_perdida:.2f} fichas"

    if capital_actual < capital_minimo:
        return False, f"{resultado}. Capital mínimo alcanzado, bot se desactiva.", ganancia_perdida, capital_antes

    mensaje_operacion = f"Operación: {decision} | Riesgo: {riesgo} | Capital antes: {capital_antes:.2f} | {resultado} | Capital ahora: {capital_actual:.2f}"
    return True, mensaje_operacion, ganancia_perdida, capital_antes

# -----------------------
# FUNCIONES DE REPORTE
# -----------------------
async def enviar_reporte(mensaje_extra=""):
    global capital_actual
    mensaje = f"Reporte de Bot:\nCapital actual: {capital_actual:.2f} fichas.\n{mensaje_extra}"
    async with app.bot:
        await app.bot.send_message(chat_id=CHAT_ID, text=mensaje)
    with open(FILENAME, "a") as f:
        f.write(f"{datetime.now()} - {mensaje}\n")

# -----------------------
# HANDLER DE COMANDOS TELEGRAM
# -----------------------
async def saludo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"¡Hola! Capital actual: {capital_actual:.2f} fichas.")

async def que_tal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Capital actual: {capital_actual:.2f} fichas.")

# -----------------------
# LOOP PRINCIPAL ASÍNCRONO
# -----------------------
async def trading_loop():
    global capital_actual
    contador_reporte = 0
    while True:
        prob_polymarket = await obtener_datos_polymarket()
        decision, riesgo = decidir_operacion(prob_polymarket)
        activo, mensaje_operacion, _, _ = ejecutar_operacion(decision, riesgo)
        print(mensaje_operacion)  # para ver operaciones en logs

        contador_reporte += 1
        if contador_reporte >= 5:
            await enviar_reporte(mensaje_operacion)
            contador_reporte = 0

        if not activo:
            await enviar_reporte(mensaje_operacion)
            break

        await asyncio.sleep(60)  # 1 min por iteración

# -----------------------
# CONFIGURACIÓN DEL BOT TELEGRAM
# -----------------------
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("hola", saludo))
app.add_handler(CommandHandler("quetal", que_tal))

# -----------------------
# EJECUCIÓN CONCURRENTE
# -----------------------
async def main():
    # Ejecuta el trading loop junto con el polling de Telegram
    await asyncio.gather(
        trading_loop(),
        app.run_polling()
    )

if __name__ == "__main__":
    asyncio.run(main())
