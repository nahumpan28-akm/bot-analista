import os
import random
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

capital = 1500.0

# 🧠 Simulación
def operar():
    global capital

    riesgo = random.choice(["muy bajo", "bajo"])
    cambio = random.uniform(-15, 15) if riesgo == "muy bajo" else random.uniform(-50, 50)

    capital_antes = capital
    capital += cambio

    if cambio >= 0:
        accion = "COMPRAR"
        resultado = f"Ganó {cambio:.2f}"
    else:
        accion = "VENDER"
        resultado = f"Perdió {abs(cambio):.2f}"

    return (
        f"📊 Operación\n"
        f"Acción: {accion}\n"
        f"Riesgo: {riesgo}\n"
        f"Capital antes: {capital_antes:.2f}\n"
        f"{resultado}\n"
        f"Capital actual: {capital:.2f}"
    )

# 🤖 Responder mensajes
async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.lower()

    if "hola" in texto:
        await update.message.reply_text("👋 Hola, estoy activo")

    elif "status" in texto:
        await update.message.reply_text(f"💰 Capital actual: {capital:.2f}")

    else:
        await update.message.reply_text("Comandos: hola / status")

# 🔁 Loop automático
async def ciclo(context: ContextTypes.DEFAULT_TYPE):
    mensaje = operar()
    try:
        await context.bot.send_message(chat_id=CHAT_ID, text=mensaje)
    except Exception as e:
        print("Error:", e)

# ▶️ MAIN SIN asyncio.run()
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # responder mensajes
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

    # ejecutar cada 30 segundos
    app.job_queue.run_repeating(ciclo, interval=30, first=5)

    print("Bot corriendo...")
    app.run_polling()

# ▶️ Ejecutar
if __name__ == "__main__":
    main()
