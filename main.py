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
# FUNCIONES DE TRADING
# -----------------------
async def obtener_probabilidad():
    """Simula probabilidad de mercado"""
    return random.uniform(0.3, 0.8)

def decidir_operacion(prob):
    """Decide si comprar o vender según probabilidad y riesgo"""
    riesgo = random.choice(["muy bajo", "bajo", "medio", "alto"])
    if ((riesgo == "muy bajo" and prob > 0.55) or
        (riesgo == "bajo" and prob > 0.6) or
        (riesgo == "medio" and prob > 0.65) or
        (riesgo == "alto" and prob > 0.75)):
        decision = "comprar"
    else:
        decision = "vender"
    return decision, riesgo

def ejecutar_operacion(decision, riesgo):
    """Ejecuta la operación y calcula ganancia o pérdida"""
    global capital_actual
    factor = {"muy bajo": 0.02, "bajo": 0.04, "medio": 0.07, "alto": 0.12}
    cantidad = capital_actual * factor[riesgo]
    resultado_num = cantidad * random.uniform(0.9, 1.1)
    capital_antes = capital_actual

    if decision == "comprar":
        capital_actual += resultado_num
        resultado = f"Ganó {resultado_num:.2f} fichas"
    else:
        capital_actual -= resultado_num
        resultado = f"Perdió {resultado_num:.2f} fichas"

    mensaje = f"Operación: {decision} | Riesgo: {riesgo} | Capital antes: {capital_antes:.2f} | {resultado} | Capital ahora: {capital_actual:.2f}"
    return capital_actual >= capital_minimo, mensaje

# -----------------------
# REPORTE
# -----------------------
async def enviar_reporte(app, mensaje_extra=""):
    """Envía reporte al chat y guarda en historial"""
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
# LOOP DE TRADING
# -----------------------
async def trading_loop(app):
    """Loop principal de operaciones"""
    global capital_actual
    while capital_actual >= capital_minimo:
        prob = await obtener_probabilidad()
        decision, riesgo = decidir_operacion(prob)
        activo, mensaje = ejecutar_operacion(decision, riesgo)
        print(mensaje)
        await enviar_reporte(app, mensaje)
        if not activo:
            print("Capital muy bajo. Bot detenido.")
            await enviar_reporte(app, "Capital muy bajo. Bot detenido.")
            break
        await asyncio.sleep(60)  # espera 1 minuto por iteración

# -----------------------
# EJECUCIÓN PRINCIPAL
# -----------------------
async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("hola", saludo))
    asyncio.create_task(trading_loop(app))
    await app.run_polling()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError:
        # Si ya hay un loop activo, lo reutilizamos
        loop = asyncio.get_event_loop()
        loop.create_task(main())
