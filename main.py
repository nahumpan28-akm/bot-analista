import os
import asyncio
import random
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# -----------------------
# CONFIGURACIÓN DEL BOT
# -----------------------
TOKEN = os.getenv("TELEGRAM_TOKEN")
if TOKEN is None:
    raise Exception("Debes definir TELEGRAM_TOKEN")
CHAT_ID_ENV = os.getenv("TELEGRAM_CHAT_ID")
if CHAT_ID_ENV is None:
    raise Exception("Debes definir TELEGRAM_CHAT_ID")
CHAT_ID = int(CHAT_ID_ENV)

# -----------------------
# CAPITAL INICIAL
# -----------------------
capital = 1500
capital_minimo = 1000
capital_actual = capital
FILENAME = "historial.txt"

# -----------------------
# FUNCIONES DE TRADING
# -----------------------
async def obtener_datos_polymarket():
    """Simula probabilidad de mercado en Polymarket"""
    return random.uniform(0.3, 0.8)

def decidir_operacion(prob_polymarket):
    """Decide si comprar o vender según riesgo y probabilidad"""
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
    """Actualiza el capital según la operación"""
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

# -----------------------
# FUNCIONES DE REPORTE
# -----------------------
async def enviar_reporte(app, mensaje_extra=""):
    """Envía reporte al chat y lo guarda en historial"""
    global capital_actual
    mensaje = f"Reporte de Bot:\nCapital actual: {capital_actual:.2f} fichas.\n{mensaje_extra}"
    await app.bot.send_message(chat_id=CHAT_ID, text=mensaje)
    with open(FILENAME, "a") as f:
        f.write(f"{datetime.now()} - {mensaje}\n")

# -----------------------
# HANDLERS DE TELEGRAM
# -----------------------
async def saludo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responde a /hola"""
    await update.message.reply_text(f"¡Hola! Capital actual: {capital_actual:.2f} fichas.")

async def que_tal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responde a /quetal"""
    await update.message.reply_text(f"Capital actual: {capital_actual:.2f} fichas.")

# -----------------------
# LOOP PRINCIPAL DE TRADING
# -----------------------
async def trading_loop(app):
    global capital_actual
    contador = 0
    while capital_actual >= capital_minimo:
        prob = await obtener_datos_polymarket()
        decision, riesgo = decidir_operacion(prob)
        activo, mensaje = ejecutar_operacion(decision, riesgo)
        print(mensaje)  # logs locales
        contador += 1
        # Enviar reporte cada 5 iteraciones (~5 min)
        if contador >= 5 or not activo:
            await enviar_reporte(app, mensaje)
            contador = 0
        # Si capital muy bajo, detener el bot
        if not activo:
            print("Capital muy bajo. Bot detenido.")
            break
        await asyncio.sleep(60)  # 1 minuto por iteración

# -----------------------
# CONFIGURACIÓN DEL BOT
# -----------------------
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("hola", saludo))
app.add_handler(CommandHandler("quetal", que_tal))

# Inicia trading_loop como tarea cuando el bot está listo
async def start_trading(app):
    asyncio.create_task(trading_loop(app))

app.post_init = start_trading  # asegura que el loop ya está activo

# -----------------------
# EJECUCIÓN
# -----------------------
if __name__ == "__main__":
    # Solo un polling, sin asyncio.run()
    app.run_polling()
