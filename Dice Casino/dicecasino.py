import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Load environment variables from .env file
load_dotenv()

# Telegram bot token and Infura Project ID directly embedded
TELEGRAM_BOT_TOKEN = "7000894405:AAF6FS6vQlNE6vmZ1pSFkZw9TgmhYA8AmYw"
INFURA_PROJECT_ID = "e3898fac3b0b4268b6af455dd415f603"

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Deposit Crypto", callback_data='deposit')],
        [InlineKeyboardButton("Play Dice Game", callback_data='dice')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Hello! Welcome to the Crypto Bot. What would you like to do?', reply_markup=reply_markup)

# Callback handler for button presses
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'deposit':
        await query.edit_message_text(text="Your wallet address is: 0xYourWalletAddress")
        # Add logic to check for deposits and update the balance here
    elif query.data == 'dice':
        result = "You rolled a 6!"  # Example result
        await query.edit_message_text(text=f"Dice Game Result: {result}")

# Main function to start the bot
def main() -> None:
    # Initialize the application with the bot token
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add handlers for start command and button presses
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
