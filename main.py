import telebot
from flask import Flask, request
import json
import os

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# -----------------------------
# Load games.json
# -----------------------------
def load_games():
    with open("games.json", "r", encoding="utf-8") as f:
        return json.load(f)

# -----------------------------
# Admin ID
# -----------------------------
ADMIN_ID = 123456789  # آیدی عددی خودت را بگذار

# -----------------------------
# Start Command
# -----------------------------
@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message, "سلام! نام بازی را بفرست تا جستجو کنم 🎮")

# -----------------------------
# Admin Panel
# -----------------------------
@bot.message_handler(commands=["admin"])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.send_message(message.chat.id,
                     "پنل مدیریت:\n/add - افزودن بازی\n/delete - حذف بازی\n/list - لیست بازی‌ها")

# -----------------------------
# Add Game
# -----------------------------
@bot.message_handler(commands=["add"])
def add_game(message):
    if message.from_user.id != ADMIN_ID:
        return
    msg = bot.send_message(message.chat.id, "نام بازی را وارد کن:")
    bot.register_next_step_handler(msg, save_game)

def save_game(message):
    name = message.text
    games = load_games()
    games.append({"name": name})
    with open("games.json", "w", encoding="utf-8") as f:
        json.dump(games, f, ensure_ascii=False, indent=2)
    bot.send_message(message.chat.id, "بازی اضافه شد ✔️")

# -----------------------------
# Delete Game
# -----------------------------
@bot.message_handler(commands=["delete"])
def delete_game(message):
    if message.from_user.id != ADMIN_ID:
        return
    msg = bot.send_message(message.chat.id, "نام بازی برای حذف:")
    bot.register_next_step_handler(msg, remove_game)

def remove_game(message):
    name = message.text
    games = load_games()
    games = [g for g in games if g["name"] != name]
    with open("games.json", "w", encoding="utf-8") as f:
        json.dump(games, f, ensure_ascii=False, indent=2)
    bot.send_message(message.chat.id, "بازی حذف شد ❌")

# -----------------------------
# Search Game
# -----------------------------
@bot.message_handler(func=lambda m: True)
def search(message):
    query = message.text.lower()
    games = load_games()
    results = [g["name"] for g in games if query in g["name"].lower()]

    if results:
        bot.reply_to(message, "\n".join(results))
    else:
        bot.reply_to(message, "چیزی پیدا نشد ❗")

# -----------------------------
# Webhook Route
# -----------------------------
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

# -----------------------------
# Root
# -----------------------------
@app.route("/", methods=["GET"])
def home():
    return "Bot is running"

# -----------------------------
# Run (Replit requires port 8080)
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
