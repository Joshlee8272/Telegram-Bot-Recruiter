import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
import threading

# === CONFIG ===
TOKEN = "8430159328:AAEgNPMo1HDsCHAY17NTDiYj2N-wfX39t7c"  # Replace with your bot token
OWNER_ID = 7301067810      # Replace with your Telegram ID
CHANNEL_LINK = "https://t.me/+Z3UYgD14if43NTJl"  # Replace with your channel link

bot = telebot.TeleBot(TOKEN)

# Store applications temporarily
applications = {}

# === START COMMAND ===
@bot.message_handler(commands=['start'])
def start(msg):
    user_id = msg.chat.id
    applications[user_id] = {}
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("✅ Yes", callback_data="dev_yes"),
        InlineKeyboardButton("❌ No", callback_data="dev_no")
    )
    bot.send_message(
        user_id,
        "👋 *Welcome to Roblox Dev Recruiter Bot!*\n\n"
        "We only accept *real Roblox developers* into our community.\n\n"
        "❓ Are you a *Roblox Game Developer?*",
        reply_markup=markup,
        parse_mode="Markdown"
    )

# === HANDLE RESPONSES ===
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    user_id = call.message.chat.id

    # Q1 - Are you developer?
    if call.data == "dev_yes":
        applications[user_id]["developer"] = "Yes"
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("✅ Yes", callback_data="own_yes"),
            InlineKeyboardButton("❌ No", callback_data="own_no")
        )
        bot.edit_message_text(
            "🎮 Great! Next question:\n\n"
            "❓ Do you *own a Roblox game* (published or in-progress)?",
            user_id,
            call.message.message_id,
            reply_markup=markup,
            parse_mode="Markdown"
        )

    elif call.data == "dev_no":
        applications[user_id]["developer"] = "No"
        bot.edit_message_text(
            "❌ Sorry, only *Roblox developers* are allowed to join.",
            user_id,
            call.message.message_id,
            parse_mode="Markdown"
        )

    # Q2 - Own a Roblox game?
    elif call.data in ["own_yes", "own_no"]:
        applications[user_id]["owns_game"] = "Yes" if call.data == "own_yes" else "No"
        rules_text = (
            "📜 *Channel Rules*\n\n"
            "1️⃣ Must be a *Roblox Developer* (scripter, builder, UI, etc.)\n"
            "2️⃣ Respect everyone, no toxicity 🚫\n"
            "3️⃣ Only share *safe & useful* Roblox files (no exploits/malware)\n"
            "4️⃣ No spam or self-promotion 🚫\n"
            "5️⃣ Credit creators if you share their work ✨\n"
            "6️⃣ Admins’ decision is final 👑\n\n"
            "❓ Are you willing to *follow our rules?*"
        )
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("✅ Yes, I Agree", callback_data="rules_yes"),
            InlineKeyboardButton("❌ No", callback_data="rules_no")
        )
        bot.edit_message_text(
            rules_text,
            user_id,
            call.message.message_id,
            reply_markup=markup,
            parse_mode="Markdown"
        )

    # Q3 - Accept rules?
    elif call.data == "rules_yes":
        applications[user_id]["rules"] = "Yes"
        bot.edit_message_text(
            "✅ Thank you! 🎉\n\n"
            "Your application has been submitted and will be reviewed by our team.",
            user_id,
            call.message.message_id,
            parse_mode="Markdown"
        )

        # Send application to OWNER for review
        app = applications[user_id]
        app_text = (
            "📨 *New Application Submitted*\n\n"
            f"👤 User: @{call.from_user.username or 'No Username'}\n"
            f"🆔 User ID: {user_id}\n\n"
            f"👾 Developer: {app['developer']}\n"
            f"🎮 Owns Game: {app['owns_game']}\n"
            f"📜 Agreed Rules: {app['rules']}\n\n"
            "Do you want to approve this application?"
        )
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("✅ Accept", callback_data=f"accept_{user_id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user_id}")
        )
        bot.send_message(OWNER_ID, app_text, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "rules_no":
        applications[user_id]["rules"] = "No"
        bot.edit_message_text(
            "❌ You must agree to the rules to join our community.",
            user_id,
            call.message.message_id,
            parse_mode="Markdown"
        )

    # === OWNER DECISIONS ===
    elif call.data.startswith("accept_"):
        target_id = int(call.data.split("_")[1])
        bot.send_message(
            target_id,
            f"🎉 *Congratulations!* 🎉\n\n"
            f"Your application has been *accepted* ✅\n\n"
            f"Here’s the channel link: 👉 {CHANNEL_LINK}",
            parse_mode="Markdown"
        )
        bot.edit_message_text(
            "✅ Application has been *accepted*. The user has received the channel link.",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown"
        )

    elif call.data.startswith("reject_"):
        target_id = int(call.data.split("_")[1])
        bot.send_message(
            target_id,
            "❌ Sorry, your application has been *rejected*.\n\n"
            "You may try again later if you meet the requirements.",
            parse_mode="Markdown"
        )
        bot.edit_message_text(
            "🚫 Application has been *rejected*.",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown"
        )

# === FLASK KEEP-ALIVE SERVER ===
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host="0.0.0.0", port=8080)

def start_bot():
    bot.infinity_polling()

# Run bot + webserver in parallel
if __name__ == "__main__":
    threading.Thread(target=run).start()
    threading.Thread(target=start_bot).start()