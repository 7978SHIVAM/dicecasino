import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import random

# Load environment variables from .env file
load_dotenv()

# Telegram bot token
TELEGRAM_BOT_TOKEN = "7000894405:AAF6FS6vQlNE6vmZ1pSFkZw9TgmhYA8AmYw"

# In-memory user data (use a database for production)
users = {}

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id

    if user_id not in users:
        users[user_id] = {"balance": 1000}  # Initialize user with a balance of 1000 units

    keyboard = [
        [InlineKeyboardButton("Check Balance", callback_data='balance')],
        [InlineKeyboardButton("Play Dice Game", callback_data='dice')],
        [InlineKeyboardButton("Deposit Crypto", callback_data='deposit')],
        [InlineKeyboardButton("Withdraw Crypto", callback_data='withdraw')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Welcome to the Casino Bot! What would you like to do?', reply_markup=reply_markup)

# Callback handler for button presses
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id

    await query.answer()

    if query.data == 'balance':
        balance = users[user_id]["balance"]
        await query.edit_message_text(text=f"Your current balance is: {balance} units")

    elif query.data == 'dice':
        await query.edit_message_text(text="Please enter the amount you want to bet:")

    elif query.data == 'deposit':
        # Logic to provide deposit address and monitor transactions
        await query.edit_message_text(text="Your deposit address is: ``0x3A035f8B7215fEb5c68c74665Fbaf9255681A8FB`` ")
    
    elif query.data == 'withdraw':
        await query.edit_message_text(text="Please enter the amount you want to withdraw:")

# Handler for processing bets
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_message = update.message.text

    if user_id not in users:
        await update.message.reply_text("Please start the bot with /start")
        return

    try:
        bet_amount = int(user_message)
    except ValueError:
        await update.message.reply_text("Please enter a valid number for your bet.")
        return

    if bet_amount > users[user_id]["balance"]:
        await update.message.reply_text("You don't have enough balance to place this bet.")
        return

    # Simulate dice roll (1-6)
    roll = random.randint(1, 6)

    if roll > 3:
        users[user_id]["balance"] += bet_amount  # Win: double the bet amount
        result = f"You rolled a {roll}. You win {bet_amount} units! Your new balance is {users[user_id]['balance']} units."
    else:
        users[user_id]["balance"] -= bet_amount  # Lose: subtract the bet amount
        result = f"You rolled a {roll}. You lose {bet_amount} units. Your new balance is {users[user_id]['balance']} units."

    await update.message.reply_text(result)

# Main function to start the bot
def main() -> None:
    # Initialize the application with the bot token
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add handlers for start command, button presses, and betting
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
