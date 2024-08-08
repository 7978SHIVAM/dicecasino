import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

# Load environment variables from .env file
load_dotenv()

# Retrieve Telegram bot token and Infura Project ID from environment variables
TELEGRAM_BOT_TOKEN = os.getenv('7000894405:AAF6FS6vQlNE6vmZ1pSFkZw9TgmhYA8AmYw')
INFURA_PROJECT_ID = os.getenv('e3898fac3b0b4268b6af455dd415f603')

# Start command handler
def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Deposit Crypto", callback_data='deposit')],
        [InlineKeyboardButton("Play Dice Game", callback_data='dice')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Hello! Welcome to the Crypto Bot. What would you like to do?', reply_markup=reply_markup)

# Callback handler for button presses
def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    if query.data == 'deposit':
        query.edit_message_text(text="Your wallet address is: 0x3A035f8B7215fEb5c68c74665Fbaf9255681A8FB")
        # You can add logic here to check for deposits and update the balance
    elif query.data == 'dice':
        # Dummy dice game logic, you can implement actual logic as needed
        result = "You rolled a 6!"  # Example result
        query.edit_message_text(text=f"Dice Game Result: {result}")

# Main function to start the bot
def main() -> None:
    # Initialize the updater and dispatcher
    updater = Updater(TELEGRAM_BOT_TOKEN)
    dispatcher = updater.dispatcher

    # Add handlers for start command and button presses
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(button))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
