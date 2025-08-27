import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ====== CONFIG ======
TOKEN = "430159328:AAEgNPMo1HDsCHAY17NTDiYj2N-wfX39t7c"  # Replace with your bot token
ADMIN_ID = 7301067810     # Replace with your Telegram ID
CHANNEL_LINK = "https://t.me/+Z3UYgD14if43NTJl"  # Replace with your TG channel link
# ====================

# Track user states and accepted users
user_states = {}
applications = {}
accepted_users = set()

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in accepted_users:
        await update.message.reply_text("✅ You are already accepted and have access to the channel.")
        return
    
    keyboard = [[InlineKeyboardButton("Yes ✅", callback_data="dev_yes"),
                 InlineKeyboardButton("No ❌", callback_data="dev_no")]]
    await update.message.reply_text("👋 Welcome!\n\nAre you a Roblox Game Developer?", reply_markup=InlineKeyboardMarkup(keyboard))
    user_states[user_id] = "Q1"

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if user_id in accepted_users:
        await query.edit_message_text("✅ You are already accepted.")
        return

    if query.data == "dev_yes":
        applications[user_id] = {"developer": "Yes"}
        keyboard = [[InlineKeyboardButton("Yes ✅", callback_data="own_yes"),
                     InlineKeyboardButton("No ❌", callback_data="own_no")]]
        await query.edit_message_text("Do you own some Roblox Game?", reply_markup=InlineKeyboardMarkup(keyboard))
        user_states[user_id] = "Q2"
    
    elif query.data == "dev_no":
        applications[user_id] = {"developer": "No"}
        await query.edit_message_text("❌ Sorry, this group is only for Roblox developers.")

    elif query.data == "own_yes":
        applications[user_id]["owns_game"] = "Yes"
        await query.edit_message_text("📝 Please write a short letter about yourself and your Roblox projects.")
        user_states[user_id] = "LETTER"
    
    elif query.data == "own_no":
        applications[user_id]["owns_game"] = "No"
        await query.edit_message_text("📝 Please write a short letter about yourself and your Roblox interest.")
        user_states[user_id] = "LETTER"
    
    elif query.data == "rules_yes":
        applications[user_id]["rules"] = "Agreed"
        # Send application to admin
        text = f"📩 New Application from @{query.from_user.username or query.from_user.first_name} (ID: {user_id})\n\n"
        for k, v in applications[user_id].items():
            text += f"{k.capitalize()}: {v}\n"
        await context.bot.send_message(ADMIN_ID, text + "\n\nUse /accept <id> or /reject <id>")
        await query.edit_message_text("✅ Thank you! Your application has been sent for review.")
        user_states[user_id] = "WAIT"

    elif query.data == "rules_no":
        await query.edit_message_text("❌ You must agree to the rules to continue.")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_states:
        return

    if user_states[user_id] == "LETTER":
        applications[user_id]["letter"] = update.message.text
        keyboard = [[InlineKeyboardButton("I Agree ✅", callback_data="rules_yes"),
                     InlineKeyboardButton("I Disagree ❌", callback_data="rules_no")]]
        rules_text = (
            "📜 Rules for Joining:\n\n"
            "1. Must be a Roblox Game Developer.\n"
            "2. Respect all members.\n"
            "3. Share files/resources responsibly.\n"
            "4. No spam or self-promotion.\n\n"
            "👉 Do you agree to follow these rules?"
        )
        await update.message.reply_text(rules_text, reply_markup=InlineKeyboardMarkup(keyboard))
        user_states[user_id] = "RULES"

# === ADMIN COMMANDS ===
async def accept(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    
    try:
        user_id = int(context.args[0])
        if user_id in accepted_users:
            await update.message.reply_text("⚠️ User already accepted.")
            return
        accepted_users.add(user_id)
        await context.bot.send_message(user_id, f"🎉 Congratulations! You have been accepted.\n\nHere is your invite link:\n{CHANNEL_LINK}")
        await update.message.reply_text("✅ User accepted and link sent.")
    except:
        await update.message.reply_text("Usage: /accept <user_id>")

async def reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        user_id = int(context.args[0])
        await context.bot.send_message(user_id, "❌ Sorry, your application was rejected.")
        await update.message.reply_text("🚫 User rejected.")
    except:
        await update.message.reply_text("Usage: /reject <user_id>")

# === MAIN ===
def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.add_handler(CommandHandler("accept", accept))
    app.add_handler(CommandHandler("reject", reject))

    app.run_polling()

if __name__ == "__main__":
    main()
