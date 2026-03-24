import os
import random
import asyncio
from telegram import Bot

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not TOKEN or not CHAT_ID:
    raise ValueError("Faltan variables de entorno")

bot = Bot(token=TOKEN)

capital = 1500.0
ultimo_mensaje = ""

# 📩 AHORA ES ASYNC
async def enviar_mensaje(mensaje):
    global ultimo_mensaje
    try:
        if mensaje != ultimo_mensaje:
            await bot.send_message(chat_id=CHAT_ID, text=mensaje)
            ultimo_mensaje = mensaje
    except Exception as e:
        print("Error:", e)

def operar():
    global capital

    riesgo = random.choice(["muy bajo", "bajo"])

    if riesgo == "muy bajo":
        cambio = random.uniform(-15, 15)
    else:
        cambio = random.uniform(-50, 50)

    capital_antes = capital
    capital += cambio

    if cambio >= 0:
        accion = "COMPRAR"
        resultado = f"Ganó {cambio:.2f}"
    else:
        accion = "VENDER"
        resultado = f"Perdió {abs(cambio):.2f}"

    mensaje = (
        f"📊 Operación\n"
        f"Acción: {accion}\n"
        f"Riesgo: {riesgo}\n"
        f"Capital antes: {capital_antes:.2f}\n"
        f"{resultado}\n"
        f"Capital actual: {capital:.2f}"
    )

    print(mensaje)
    return mensaje

# 🔁 LOOP ASYNC
async def main():
    await enviar_mensaje("🤖 Bot activo")
    print("Bot corriendo...")

    while True:
        mensaje = operar()
        await enviar_mensaje(mensaje)
        await asyncio.sleep(30)

# ▶️ EJECUTAR
asyncio.run(main())
