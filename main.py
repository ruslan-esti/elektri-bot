from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import requests
import os

TOKEN = "8569255304:AAGNVJn3ZgnNuEe3j5bzxLqCiMeI31dcvLQ"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚡ Привет!\n\nКоманды:\n/price"
    )


async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        response = requests.get(
            "https://dashboard.elering.ee/api/nps/price"
        )

        data = response.json()

        prices = data["data"]["ee"]

        if not prices:
            await update.message.reply_text("Не удалось получить цену.")
            return

        current_price = prices[0]["price"]

        await update.message.reply_text(
            f"⚡ Текущая цена:\n\n{current_price} €/MWh"
        )

    except Exception as e:
        await update.message.reply_text(
            f"Ошибка: {str(e)}"
        )


app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("price", price))

app.run_polling()
