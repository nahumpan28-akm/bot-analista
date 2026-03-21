import os
import asyncio
import requests
from telegram import Bot
from telegram.ext import ApplicationBuilder, CommandHandler

# 🔐 Variables de entorno (seguras, para no exponer el token)
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not TOKEN or not CHAT_ID:
    raise ValueError("Debes configurar TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID en las variables de entorno")

# Función para obtener datos de Binance (ejemplo simple)
def obtener_datos_binance():
    url = "https://api.binance.com/api/v3/ticker/24hr"
    response = requests.get(url)
    if response.status_code != 200:
        print("Error al obtener datos de Binance")
        return []

    data = response.json()
    # Tomamos solo los primeros 5 elementos (ejemplo)
    return data[:5] if isinstance(data, list) else []

# Función de ciclo principal que revisa oportunidades
async def ciclo(bot):
    while True:
        oportunidades = obtener_datos_binance()
        for o in oportunidades:
            mensaje = f"{o['symbol']}: Precio {o['lastPrice']}"
            await bot.send_message(chat_id=CHAT_ID, text=mensaje)
        await asyncio.sleep(60)  # espera 1 minuto

# Comando /start para Telegram
async def start(update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="¡Bot activo! 🚀")

# Función principal del bot
async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Registrar el comando /start
    app.add_handler(CommandHandler("start", start))
    
    # Crear tarea del ciclo de Binance
    asyncio.create_task(ciclo(app.bot))
    
    print("Bot activo en servidor 🚀")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
