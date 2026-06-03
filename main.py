from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import requests
import os
from datetime import datetime

TOKEN = os.getenv("BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚡ Привет!\n\n"
        "Команды:\n"
        "/price\n"
        "/debug"
    )


async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        response = requests.get(
            "https://dashboard.elering.ee/api/nps/price"
        )

        data = response.json()
        prices = data["data"]["ee"]

        if not prices:
            await update.message.reply_text(
                "Не удалось получить цену."
            )
            return

        now = int(datetime.now().timestamp())

        current_price = None

        for item in prices:
            timestamp = item["timestamp"]

            if timestamp <= now < timestamp + 3600:
                current_price = item["price"]
                break

        if current_price is None:
            current_price = prices[0]["price"]

        cents = round(current_price / 10, 2)

        if cents < 5:
            icon = "🟢"
            text = "Очень дёшево"
        elif cents < 10:
            icon = "🟡"
            text = "Хорошая цена"
        elif cents < 20:
            icon = "🟠"
            text = "Средняя цена"
        else:
            icon = "🔴"
            text = "Дорого"

        await update.message.reply_text(
            f"⚡ Электричество сейчас\n\n"
            f"{icon} {cents} c/kWh\n"
            f"📊 {text}"
        )

    except Exception as e:
        await update.message.reply_text(
            f"Ошибка: {str(e)}"
        )


async def debug(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        response = requests.get(
            "https://dashboard.elering.ee/api/nps/price"
        )

        data = response.json()
        prices = data["data"]["ee"]

        text = ""

        for item in prices[:10]:
            text += (
                f"TS: {item['timestamp']}\n"
                f"PRICE: {item['price']}\n\n"
            )

        await update.message.reply_text(text)

    except Exception as e:
        await update.message.reply_text(
            f"Ошибка: {str(e)}"
        )


app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("price", price))
app.add_handler(CommandHandler("debug", debug))

app.run_polling()
