from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import requests
import os
from datetime import datetime

TOKEN = os.getenv("BOT_TOKEN")


def get_prices():
    response = requests.get(
        "https://dashboard.elering.ee/api/nps/price"
    )

    data = response.json()
    return data["data"]["ee"]


def get_status(price):
    if price < 5:
        return "🟢", "Очень выгодно"
    elif price < 10:
        return "🟡", "Хорошая цена"
    elif price < 15:
        return "🟠", "Средняя цена"
    else:
        return "🔴", "Дорого"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚡ ElektriHindBot\n\n"
        "Доступные команды:\n\n"
        "/price - Цена сейчас\n"
        "/best - Лучший час\n"
        "/top3 - ТОП-3 часа"
    )


async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        prices = get_prices()

        current_price = prices[-1]["price"] / 10

        icon, text = get_status(current_price)

        await update.message.reply_text(
            f"⚡ Электричество сейчас\n\n"
            f"{icon} {current_price:.2f} c/kWh\n\n"
            f"📊 {text}"
        )

    except Exception as e:
        await update.message.reply_text(
            f"Ошибка: {str(e)}"
        )


async def best(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        prices = get_prices()

        now = int(datetime.now().timestamp())

        best_price = None
        best_index = None

        for i in range(len(prices) - 3):

            if prices[i]["timestamp"] < now:
                continue

            avg = (
                prices[i]["price"] +
                prices[i + 1]["price"] +
                prices[i + 2]["price"] +
                prices[i + 3]["price"]
            ) / 4

            if best_price is None or avg < best_price:
                best_price = avg
                best_index = i

        if best_index is None:
            await update.message.reply_text(
                "Нет данных о будущих ценах."
            )
            return

        ts = prices[best_index]["timestamp"]

        start_time = datetime.fromtimestamp(ts)
        end_time = datetime.fromtimestamp(ts + 3600)

        await update.message.reply_text(
            f"🏆 Лучшее время впереди\n\n"
            f"⏰ {start_time.strftime('%H:%M')}–{end_time.strftime('%H:%M')}\n\n"
            f"🟢 {best_price / 10:.2f} c/kWh"
        )

    except Exception as e:
        await update.message.reply_text(
            f"Ошибка: {str(e)}"
        )


async def top3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        prices = get_prices()

        now = int(datetime.now().timestamp())

        hours = []

        for i in range(len(prices) - 3):

            if prices[i]["timestamp"] < now:
                continue

            avg = (
                prices
