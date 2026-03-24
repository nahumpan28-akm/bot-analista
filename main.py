import telebot
import random
import time
import os

# 🔐 Variables de entorno (SEGURIDAD)
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Validación básica
if not TOKEN or not CHAT_ID:
    raise ValueError("Faltan TOKEN o CHAT_ID en variables de entorno")

bot = telebot.TeleBot(TOKEN)

# Capital inicial
capital = 1500.0

# Para evitar spam repetido
ultimo_mensaje = ""

# 📩 Función para enviar mensajes
def enviar_mensaje(mensaje):
    global ultimo_mensaje
    try:
        # Evita enviar el mismo mensaje repetido
        if mensaje != ultimo_mensaje:
            bot.send_message(CHAT_ID, mensaje)
            ultimo_mensaje = mensaje
    except Exception as e:
        print("Error enviando mensaje:", e)

# 🧠 Simulación de operación
def operar():
    global capital

    riesgos = ["muy bajo", "bajo"]
    riesgo = random.choice(riesgos)

    if riesgo == "muy bajo":
        cambio = random.uniform(-15, 15)
    else:
        cambio = random.uniform(-50, 50)

    capital_antes = capital
    capital += cambio

    if cambio >= 0:
        resultado = f"Ganó {cambio:.2f} fichas"
        accion = "COMPRAR"
    else:
        resultado = f"Perdió {abs(cambio):.2f} fichas"
        accion = "VENDER"

    mensaje = (
        f"📊 Operación\n"
        f"Acción: {accion}\n"
        f"Riesgo: {riesgo}\n"
        f"Capital antes: {capital_antes:.2f}\n"
        f"{resultado}\n"
        f"Capital actual: {capital:.2f}"
    )

    print(mensaje)
    enviar_mensaje(mensaje)

# 🔁 Loop principal
def main():
    enviar_mensaje("🤖 Bot de trading iniciado correctamente")
    print("Bot activo...")

    while True:
        operar()
        time.sleep(30)  # más realista (30 segundos)

# ▶️ Ejecutar
if __name__ == "__main__":
    main()
