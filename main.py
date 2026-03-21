import os
import asyncio
import requests
import random
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("TELEGRAM_TOKEN")
if TOKEN is None:
    raise Exception("Debes definir TELEGRAM_TOKEN")
CHAT_ID_ENV = os.getenv("TELEGRAM_CHAT_ID")
if CHAT_ID_ENV is None:
    raise Exception("Debes definir TELEGRAM_CHAT_ID")
CHAT_ID = int(CHAT_ID_ENV)

capital = 1500
capital_minimo = 1000
capital_actual = capital
FILENAME = "historial.txt"

async def obtener_datos_polymarket():
    return random.uniform(0.3, 0.8)

def decidir_operacion(prob_polymarket):
    riesgo = random.choice(["muy bajo", "bajo", "medio", "alto"])
    if ((riesgo == "muy bajo" and prob_polymarket > 0.55) or
        (riesgo == "bajo" and prob_polymarket > 0.6) or
        (riesgo == "medio" and prob_polymarket > 0.65) or
        (riesgo == "alto" and prob_polymarket > 0.75)):
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

    mensaje = f"Operación: {decision} | Riesgo: {riesgo} | Capital antes: {capital_antes:.2f} | {resultado} | Capital ahora: {capital_actual:.2f}"
    return capital_actual >= capital_minimo, mensaje

async def enviar_reporte(app, mensaje_extra=""):
    global capital_actual
    mensaje = f"Reporte de Bot:\nCapital actual: {capital_actual:.2f} fichas.\n{mensaje_extra}"
    await app.bot.send_message(chat_id=CHAT_ID, text=mensaje)
    with open(FILENAME, "a") as f:
        f.write(f"{datetime.now()} - {mensaje}\n")

# Handlers de Telegram
async def saludo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"¡Hola! Capital actual: {capital_actual:.2f} fichas.")

async def que_tal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Capital actual: {capital_actual:.2f} fichas.")

# Loop de trading
async def trading_loop(app):
    global capital_actual
    contador = 0
    while capital_actual >= capital_minimo:
        prob = await obtener_datos_polymarket()
        decision, riesgo = decidir_operacion(prob)
        activo, mensaje = ejecutar_operacion(decision, riesgo)
        print(mensaje)  # logs locales
        contador += 1
        if contador >= 5:  # reporte cada 5 iteraciones
            await enviar_reporte(app, mensaje)
            contador = 0
        await asyncio.sleep(60)

# Configuración del bot
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("hola", saludo))
app.add_handler(CommandHandler("quetal", que_tal))

# Inicia trading_loop como tarea en el mismo event loop
async def start_trading(app):
    asyncio.create_task(trading_loop(app))

# Ejecuta bot
if __name__ == "__main__":
    app.post_init = start_trading  # esto asegura que el loop ya está activo
    app.run_polling()
