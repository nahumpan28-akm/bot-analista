import os
import random
import asyncio
from telegram import Update, Bot
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
        await update.message.reply_text("No entendí, prueba: hola / status")

# 🔁 Loop automático
async def ciclo(bot: Bot):
    while True:
        mensaje = operar()
        try:
            await bot.send_message(chat_id=CHAT_ID, text=mensaje)
        except Exception as e:
            print("Error:", e)

        await asyncio.sleep(30)

# ▶️ MAIN
async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

    bot = Bot(token=TOKEN)

    # Ejecutar ciclo en paralelo
    asyncio.create_task(ciclo(bot))

    print("Bot corriendo...")
    await app.run_polling()

# ▶️ Ejecutar
asyncio.run(main())
