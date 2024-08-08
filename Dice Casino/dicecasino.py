from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext
from web3 import Web3

# Initialize the Web3 instance (Ethereum blockchain)
w3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID"))

# Replace with your wallet address
WALLET_ADDRESS = "LTcAo5Xa1PRRdnNC7aw1JfQ7dAm2DUC7PB"

# Start command handler
def start(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    update.message.reply_text(
        f"Hello {user.first_name}! Welcome to our bot. How would you like to proceed?",
        reply_markup=main_menu_keyboard()
    )

# Main menu keyboard
def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("Deposit LTC ", callback_data='deposit')],
        [InlineKeyboardButton("Play Dice Game", callback_data='play_dice')],
    ]
    return InlineKeyboardMarkup(keyboard)

# Callback query handler
def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    
    if query.data == 'deposit':
        query.edit_message_text(text=f"Please deposit your LTC to the following address:\n{WALLET_ADDRESS}")
    elif query.data == 'play_dice':
        if check_balance():
            dice_roll = context.bot.send_dice(chat_id=query.message.chat_id).dice.value
            query.edit_message_text(text=f"🎲 You rolled a {dice_roll}!")
        else:
            query.edit_message_text(text="Insufficient balance! Please deposit LTC first.")

# Check balance (dummy implementation)
def check_balance():
    # Implement balance check logic here
    return True  # Assuming balance is always available for this example

# Message handler for depositing
def deposit_crypto(update: Update, context: CallbackContext) -> None:
    # Here you would normally verify the deposit by checking transactions in the wallet
    update.message.reply_text("Thank you! Your deposit has been confirmed.")
    update.message.reply_text("Your new balance has been added.")

# Error handler
def error(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('An error occurred!')

def main():
    # Initialize Updater and Dispatcher
    updater = Updater("7000894405:AAF6FS6vQlNE6vmZ1pSFkZw9TgmhYA8AmYw", use_context=True)
    dispatcher = updater.dispatcher

    # Register handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, deposit_crypto))
    dispatcher.add_error_handler(error)

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
