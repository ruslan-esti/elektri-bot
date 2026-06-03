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
        "Команды:\n\n"
        "/price - Цена сейчас\n"
        "/best - Лучший час\n"
        "/top3 - ТОП-3 часа\n"
        "/when - Проверка дат API"
    )


async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        prices = get_prices()

        current_price = prices[0]["price"] / 10

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

        best_price = None
        best_timestamp = None

        for i in range(len(prices) - 3):

            avg = (
                prices[i]["price"]
                + prices[i + 1]["price"]
                + prices[i + 2]["price"]
                + prices[i + 3]["price"]
            ) / 4

            if best_price is None or avg < best_price:
                best_price = avg
                best_timestamp = prices[i]["timestamp"]

        start_time = datetime.fromtimestamp(best_timestamp)
        end_time = datetime.fromtimestamp(best_timestamp + 3600)

        await update.message.reply_text(
            f"🏆 Лучший час\n\n"
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

        hours = []

        for i in range(len(prices) - 3):

            avg = (
                prices[i]["price"]
                + prices[i + 1]["price"]
                + prices[i + 2]["price"]
                + prices[i + 3]["price"]
            ) / 4

            hours.append(
                (
                    avg,
                    prices[i]["timestamp"]
                )
            )

        hours.sort(key=lambda x: x[0])

        medals = ["🥇", "🥈", "🥉"]

        text = "🥇 ТОП-3 часа\n\n"

        for i in range(min(3, len(hours))):
            price_value, timestamp = hours[i]

            start_time = datetime.fromtimestamp(timestamp)
            end_time = datetime.fromtimestamp(timestamp + 3600)

            text += (
                f"{medals[i]} "
                f"{start_time.strftime('%H:%M')}–"
                f"{end_time.strftime('%H:%M')} → "
                f"{price_value / 10:.2f} c/kWh\n"
            )

        await update.message.reply_text(text)

    except Exception as e:
        await update.message.reply_text(
            f"Ошибка: {str(e)}"
        )


async def when(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        prices = get_prices()

        first_date = datetime.fromtimestamp(
            prices[0]["timestamp"]
        )

        last_date = datetime.fromtimestamp(
            prices[-1]["timestamp"]
        )

        await update.message.reply_text(
            f"📅 Первая запись:\n"
            f"{first_date.strftime('%d.%m.%Y %H:%M')}\n\n"
            f"📅 Последняя запись:\n"
            f"{last_date.strftime('%d.%m.
