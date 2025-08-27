import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
import threading

# === CONFIG ===
TOKEN = "8430159328:AAEgNPMo1HDsCHAY17NTDiYj2N-wfX39t7c"
OWNER_ID = 7301067810
CHANNEL_LINK = "https://t.me/+Z3UYgD14if43NTJl"

bot = telebot.TeleBot(TOKEN)

# Data storage
applications = {}
accepted_users = set()
rejected_users = set()

# === START COMMAND ===
@bot.message_handler(commands=['start'])
def start(msg):
    user_id = msg.chat.id

    if user_id in accepted_users:
        bot.send_message(user_id, f"✅ You are already accepted!\n\nHere’s the channel link: {CHANNEL_LINK}")
        return
    if user_id in rejected_users:
        bot.send_message(user_id, "🚫 You have already been rejected. You cannot reapply.")
        return

    # Require username
    if not msg.from_user.username:
        bot.send_message(user_id, "⚠️ You need a Telegram username to apply.\n\nPlease set one in Telegram settings and try again.")
        return

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

# === HELP COMMAND ===
@bot.message_handler(commands=['help'])
def help_cmd(msg):
    bot.send_message(
        msg.chat.id,
        "📖 *Bot Commands*\n\n"
        "/start - Begin application process\n"
        "/help - Show this help menu\n\n"
        "👑 *Owner Only:*\n"
        "/stats - View stats of applications\n"
        "/broadcast <message> - Send a message to all accepted users",
        parse_mode="Markdown"
    )

# === OWNER STATS COMMAND ===
@bot.message_handler(commands=['stats'])
def stats_cmd(msg):
    if msg.chat.id != OWNER_ID:
        return
    bot.send_message(
        msg.chat.id,
        f"📊 *Bot Stats*\n\n"
        f"👥 Total Applications: {len(applications)}\n"
        f"✅ Accepted: {len(accepted_users)}\n"
        f"❌ Rejected: {len(rejected_users)}",
        parse_mode="Markdown"
    )

# === BROADCAST COMMAND ===
@bot.message_handler(commands=['broadcast'])
def broadcast_cmd(msg):
    if msg.chat.id != OWNER_ID:
        return
    text = msg.text.replace("/broadcast", "").strip()
    if not text:
        bot.send_message(OWNER_ID, "⚠️ Please provide a message.\nUsage: `/broadcast Hello devs!`", parse_mode="Markdown")
        return

    count = 0
    for uid in accepted_users:
        try:
            bot.send_message(uid, f"📢 *Announcement:*\n\n{text}", parse_mode="Markdown")
            count += 1
        except:
            pass
    bot.send_message(OWNER_ID, f"✅ Broadcast sent to {count} users.")

# === HANDLE RESPONSES ===
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    user_id = call.message.chat.id

    # Developer Question
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
            user_id, call.message.message_id, reply_markup=markup, parse_mode="Markdown"
        )

    elif call.data == "dev_no":
        applications[user_id]["developer"] = "No"
        rejected_users.add(user_id)
        bot.edit_message_text(
            "❌ Sorry, only *Roblox developers* are allowed to join.",
            user_id, call.message.message_id, parse_mode="Markdown"
        )

    # Own Game Question
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
        bot.edit_message_text(rules_text, user_id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    # Rules Agreement
    elif call.data == "rules_yes":
        applications[user_id]["rules"] = "Yes"
        bot.edit_message_text(
            "✅ Thank you! 🎉\n\nYour application has been submitted and will be reviewed by our team.",
            user_id, call.message.message_id, parse_mode="Markdown"
        )

        app = applications[user_id]
        app_text = (
            "📨 *New Application Submitted*\n\n"
            f"👤 User: @{call.from_user.username}\n"
            f"🆔 User ID: {user_id}\n\n"
            f"👾 Developer: {app['developer']}\n"
            f"🎮 Owns Game: {app['owns_game']}\n"
            f"📜 Agreed Rules: {app['rules']}\n\n"
            "Do you want to approve this application?"
        )
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("✅ Accept", callback_data=f"accept_{user_id}"),
            InlineKeyboardButton("❌ Reject (Fake Dev)", callback_data=f"reject_{user_id}_fake"),
            InlineKeyboardButton("❌ Reject (No Game)", callback_data=f"reject_{user_id}_nogame"),
            InlineKeyboardButton("❌ Reject (Other)", callback_data=f"reject_{user_id}_other")
        )
        bot.send_message(OWNER_ID, app_text, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "rules_no":
        applications[user_id]["rules"] = "No"
        rejected_users.add(user_id)
        bot.edit_message_text(
            "❌ You must agree to the rules to join our community.",
            user_id, call.message.message_id, parse_mode="Markdown"
        )

    # OWNER DECISIONS
    elif call.data.startswith("accept_"):
        target_id = int(call.data.split("_")[1])
        accepted_users.add(target_id)
        bot.send_message(
            target_id,
            f"🎉 *Congratulations!* 🎉\n\nYour application has been *accepted* ✅\n\nHere’s the channel link: 👉 {CHANNEL_LINK}",
            parse_mode="Markdown"
        )
        bot.edit_message_text("✅ Application has been *accepted*.", call.message.chat.id, call.message.message_id, parse_mode="Markdown")

    elif call.data.startswith("reject_"):
        parts = call.data.split("_")
        target_id = int(parts[1])
        reason = parts[2] if len(parts) > 2 else "Not specified"
        rejected_users.add(target_id)

        bot.send_message(
            target_id,
            f"❌ Sorry, your application has been *rejected*.\n\nReason: {reason.capitalize()}",
            parse_mode="Markdown"
        )
        bot.edit_message_text(f"🚫 Application has been *rejected* ({reason}).", call.message.chat.id, call.message.message_id, parse_mode="Markdown")

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
