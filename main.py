import telebot
import random
import time

# 🔐 CONFIGURA TU BOT
TOKEN = "TU_TOKEN_DE_TELEGRAM"  # reemplaza con tu token
CHAT_ID = "TU_CHAT_ID"          # reemplaza con tu chat ID

bot = telebot.TeleBot(TOKEN)

# Capital inicial
capital = 1500.0

# Función para enviar mensajes sin async
def enviar_mensaje(mensaje):
    try:
        bot.send_message(CHAT_ID, mensaje)
    except Exception as e:
        print("Error enviando mensaje:", e)

# Función para simular una operación segura
def operar():
    global capital

    # Riesgos muy bajos y bajos
    riesgos = ["muy bajo", "bajo"]
    riesgo = random.choice(riesgos)

    # Ganancias o pérdidas según riesgo
    if riesgo == "muy bajo":
        cambio = random.uniform(-15, 15)  # riesgo mínimo
    else:
        cambio = random.uniform(-50, 50)  # riesgo bajo

    capital_antes = capital
    capital += cambio

    # Determinar si ganó o perdió
    if cambio >= 0:
        resultado = f"Gano {cambio:.2f} fichas"
    else:
        resultado = f"Perdió {abs(cambio):.2f} fichas"

    mensaje = (
        f"Operación: {'comprar' if cambio>=0 else 'vender'} | "
        f"Riesgo: {riesgo} | "
        f"Capital antes: {capital_antes:.2f} | "
        f"{resultado} | "
        f"Capital ahora: {capital:.2f}"
    )
    print(mensaje)
    enviar_mensaje(mensaje)

# Loop principal del bot
def main():
    enviar_mensaje("Bot de trading seguro iniciado...")
    print("Bot de trading seguro iniciado...")

    while True:
        operar()
        time.sleep(10)  # espera 10 segundos entre operaciones

if __name__ == "__main__":
    main()
