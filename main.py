import os
import requests
import random
import time
from datetime import datetime
import telebot  # pip install pyTelegramBotAPI==4.13.0

# -----------------------
# CONFIGURACIÓN DEL BOT
# -----------------------
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID"))
bot = telebot.TeleBot(TOKEN)

# -----------------------
# CAPITAL INICIAL
# -----------------------
capital = 1500
capital_minimo = 1000
capital_actual = capital

# -----------------------
# ARCHIVO DE HISTORIAL
# -----------------------
FILENAME = "historial.txt"

# -----------------------
# FUNCIONES DE TRADING
# -----------------------
def obtener_datos_binance():
    try:
        response = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=5)
        data = response.json()
        return float(data['price'])
    except:
        return None

def decidir_operacion(precio_binance):
    decision = random.choice(["comprar", "vender", "nada"])
    riesgo = "muy bajo"
    return decision, riesgo

def ejecutar_operacion(decision, riesgo):
    global capital_actual
    factor = {"muy bajo": 0.01}
    capital_antes = capital_actual

    if decision == "comprar":
        ganancia = capital_actual * factor[riesgo] * random.uniform(0.8, 1.2)
        capital_actual += ganancia
        mensaje = f"Operación: comprar | Riesgo: {riesgo} | Capital antes: {capital_antes:.2f} | Ganó {ganancia:.2f} fichas | Capital ahora: {capital_actual:.2f}"
    elif decision == "vender":
        perdida = capital_actual * factor[riesgo] * random.uniform(0.8, 1.2)
        capital_actual -= perdida
        mensaje = f"Operación: vender | Riesgo: {riesgo} | Capital antes: {capital_antes:.2f} | Perdió {perdida:.2f} fichas | Capital ahora: {capital_actual:.2f}"
    else:
        mensaje = f"Operación: nada | Capital: {capital_actual:.2f}"

    # Guardar historial
    with open(FILENAME, "a") as f:
        f.write(f"{datetime.now()} - {mensaje}\n")

    print(mensaje)
    try:
        bot.send_message(CHAT_ID, mensaje)
    except Exception as e:
        print(f"No se pudo enviar mensaje a Telegram: {e}")

    if capital_actual < capital_minimo:
        aviso = "Capital muy bajo. Bot detenido."
        print(aviso)
        try:
            bot.send_message(CHAT_ID, aviso)
        except:
            pass
        return False
    return True

# -----------------------
# LOOP PRINCIPAL
# -----------------------
def main():
    print("Bot de trading seguro iniciado...")
    while True:
        precio_binance = obtener_datos_binance()
        decision, riesgo = decidir_operacion(precio_binance)
        activo = ejecutar_operacion(decision, riesgo)
        if not activo:
            break
        time.sleep(60)

if __name__ == "__main__":
    main()
