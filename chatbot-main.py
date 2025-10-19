import requests  # Add this import
import aiml
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Initialize AIML kernel
kernel = aiml.Kernel()
BACKEND_URL = "http://localhost:5000/api/aiml/generate-aiml"  # Your backend URL

async def start(update: Update, context):
    await update.message.reply_text("Halo! Saya adalah chatbot PCR. Ada yang bisa saya bantu?")

def load_aiml_from_backend():
    """Fetch latest AIML from backend and reload kernel"""
    global kernel
    try:
        response = requests.get(BACKEND_URL)
        response.raise_for_status()

        with open("latest_chatbot.aiml", "w") as f:
            f.write(response.text)

        # Reinitialize the kernel instead of using a nonexistent reset()
        kernel = aiml.Kernel()
        kernel.learn("latest_chatbot.aiml")
        logging.info("Successfully reloaded AIML rules")

    except Exception as e:
        logging.error(f"Failed to update AIML: {str(e)}")

# Initial load on startup
load_aiml_from_backend()

async def reload_aiml(update: Update, context):
    """Admin command to manually reload rules"""
    load_aiml_from_backend()
    await update.message.reply_text("✅ AIML rules reloaded from backend")

async def handle_message(update: Update, context):
    user_message = update.message.text
    print(user_message)
    bot_response = kernel.respond(user_message)
    await update.message.reply_text(bot_response)

def main():
    TOKEN = "7321507910:AAH_Sg20Kn0kvV7FDS-cc-PShBJX9LAKUd0"
    application = Application.builder().token(TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("reload", reload_aiml))  # Admin command
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # # Schedule periodic reload (every 1 hour)
    # job_queue = application.job_queue
    # job_queue.run_repeating(lambda _: load_aiml_from_backend(), interval=3600, first=0)
    
    print("Bot running...")
    application.run_polling()

if __name__ == "__main__":
    main()