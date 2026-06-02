from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import requests
import os
from datetime import datetime

TOKEN = os.getenv("BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚡ Привет!\n\nКоманды:\n/price"
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
            await update.message.reply_text(
                "Не удалось определить текущую цену."
            )
            return

        price_cents = round(current_price / 10, 2)

        if price_cents < 5:
            emoji = "🟢"
            status = "Очень дёшево"
        elif price_cents < 10:
            emoji = "🟡"
            status = "Хорошая цена"
        elif price_cents < 20:
            emoji = "🟠"
            status = "Средняя цена"
        elif price_cents < 40:
            emoji = "🔴"
            status = "Дорого"
        else:
            emoji = "🚨"
            status = "Очень дорого"

        await update.message.reply_text(
            f"⚡ Электричество сейчас\n\n"
            f"{emoji} {price_cents} c/kWh\n"
            f"📊 {status}"
        )

    except Exception as e:
        await update.message.reply_text(
            f"Ошибка: {str(e)}"
        )


app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("price", price))

app.run_polling()
