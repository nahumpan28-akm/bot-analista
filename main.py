import os
import requests
import random
import time
from datetime import datetime
from telegram import Bot

# -----------------------
# CONFIGURACIÓN DEL BOT
# -----------------------
TOKEN = os.getenv("TELEGRAM_TOKEN")  # tu token como variable de entorno
CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID"))  # tu chat id como variable de entorno
bot = Bot(token=TOKEN)

# -----------------------
# CAPITAL INICIAL
# -----------------------
capital = 1500  # fichas
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
    """Obtiene el precio actual de BTC/USDT"""
    try:
        response = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=5)
        data = response.json()
        return float(data['price'])
    except:
        return None

def decidir_operacion(precio_binance):
    """Decisión segura basada en movimientos aleatorios muy conservadores"""
    # Riesgo muy bajo
    decision = random.choice(["comprar", "vender", "nada"])  # a veces no hace nada
    riesgo = "muy bajo"
    return decision, riesgo

def ejecutar_operacion(decision, riesgo):
    """Ejecuta la operación y actualiza capital"""
    global capital_actual
    factor = {"muy bajo": 0.01}  # solo riesgo muy bajo
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
    enviar_reporte(mensaje)

    if capital_actual < capital_minimo:
        aviso = "Capital muy bajo. Bot detenido."
        print(aviso)
        enviar_reporte(aviso)
        return False  # detiene bot
    return True

# -----------------------
# FUNCIONES DE REPORTE
# -----------------------
def enviar_reporte(mensaje):
    """Envía un mensaje a Telegram"""
    try:
        bot.send_message(chat_id=CHAT_ID, text=mensaje)
    except Exception as e:
        print(f"No se pudo enviar mensaje a Telegram: {e}")

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
        time.sleep(60)  # espera 1 minuto entre operaciones

if __name__ == "__main__":
    main()
