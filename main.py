import os
import random
import asyncio
from datetime import datetime
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# -----------------------
# CONFIGURACIÓN DEL BOT
# -----------------------
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID_ENV = os.getenv("TELEGRAM_CHAT_ID")
if TOKEN is None or CHAT_ID_ENV is None:
    raise Exception("Debes definir TELEGRAM_TOKEN y TELEGRAM_CHAT_ID")
CHAT_ID = int(CHAT_ID_ENV)

# -----------------------
# CAPITAL INICIAL
# -----------------------
capital_inicial = 1500
capital_minimo = 1000
capital_actual = capital_inicial
FILENAME = "historial.txt"

# -----------------------
# FUNCIONES DE TRADING CONSERVADOR
# -----------------------
async def obtener_probabilidad_segura():
    """Simula probabilidad de mercado, más segura"""
    return random.uniform(0.4, 0.7)  # más centrado, evita extremos

def decidir_operacion_segura(prob):
    """Decide si comprar o vender con riesgo muy bajo"""
    riesgo = "muy bajo"  # siempre muy bajo
    if prob > 0.52:  # solo compramos si la probabilidad es favorable
        decision = "comprar"
    else:
        decision = "vender"
    return decision, riesgo

def ejecutar_operacion_segura(decision, riesgo):
    """Ejecuta operación segura"""
    global capital_actual
    factor = {"muy bajo": 0.01}  # ganancias/pérdidas muy pequeñas
    cantidad = capital_actual * factor[riesgo]
    capital_antes = capital_actual

    if decision == "comprar":
        capital_actual += cantidad
        resultado = f"Ganó {cantidad:.2f} fichas"
    else:
        capital_actual -= cantidad
        resultado = f"Perdió {cantidad:.2f} fichas"

    mensaje = f"Operación: {decision} | Riesgo: {riesgo} | Capital antes: {capital_antes:.2f} | {resultado} | Capital ahora: {capital_actual:.2f}"
    return capital_actual >= capital_minimo, mensaje

# -----------------------
# REPORTE
# -----------------------
async def enviar_reporte(app, mensaje_extra=""):
    mensaje = f"Reporte de Bot:\nCapital actual: {capital_actual:.2f} fichas.\n{mensaje_extra}"
    await app.bot.send_message(chat_id=CHAT_ID, text=mensaje)
    with open(FILENAME, "a") as f:
        f.write(f"{datetime.now()} - {mensaje}\n")

# -----------------------
# HANDLERS
# -----------------------
async def saludo(update, context: ContextTypes.DEFAULT_TYPE):
    """Responde al comando /hola"""
    await update.message.reply_text(f"¡Hola! Capital actual: {capital_actual:.2f} fichas.")

# -----------------------
# LOOP DE TRADING SEGURA
# -----------------------
async def trading_loop_segura(app):
    global capital_actual
    while capital_actual >= capital_minimo:
        prob = await obtener_probabilidad_segura()
        decision, riesgo = decidir_operacion_segura(prob)
        activo, mensaje = ejecutar_operacion_segura(decision, riesgo)
        print(mensaje)
        await enviar_reporte(app, mensaje)
        if not activo:
            await enviar_reporte(app, "Capital muy bajo. Bot detenido.")
            break
        await asyncio.sleep(60)  # espera 1 minuto

# -----------------------
# EJECUCIÓN PRINCIPAL
# -----------------------
async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("hola", saludo))
    asyncio.create_task(trading_loop_segura(app))
    await app.run_polling()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError:
        # reutiliza loop si ya está activo
        loop = asyncio.get_event_loop()
        loop.create_task(main())
