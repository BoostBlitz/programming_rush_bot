import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Store last 2 commands per user
user_memory = {}

# Call Puter AI to get explanation
def get_deep_explanation(command):
    prompt = f"Explain in depth the programming concept: {command}"
    try:
        response = requests.post(
            "https://api.puter.com/v2/chat",
            json={
                "messages": [{"role": "user", "content": prompt}],
                "model": "gpt-4o"
            }
        )
        result = response.json()
        return result.get("choices", [{}])[0].get("message", {}).get("content", "No response.")
    except Exception as e:
        return f"❌ Error contacting AI: {e}"

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome to Programming Rush AI Help!\nUse /help <command> to learn programming deeply.")

# /help <command> handler
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args

    if not args:
        await update.message.reply_text("❗Usage: /help <programming concept>")
        return

    command = " ".join(args).strip()

    # Update memory (store last 2 commands silently)
    if user_id not in user_memory:
        user_memory[user_id] = []
    if len(user_memory[user_id]) >= 2:
        user_memory[user_id].pop(0)
    user_memory[user_id].append(command)

    # Get explanation from Puter AI
    explanation = get_deep_explanation(command)

    await update.message.reply_text(f"📘 *{command}*\n\n{explanation}", parse_mode="Markdown")

# Bot runner
def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        print("❌ BOT_TOKEN not found in environment variables.")
        return

    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    print("🚀 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
