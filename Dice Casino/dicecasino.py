import os
import asyncio
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import random

# Load environment variables from .env file
load_dotenv()

# Telegram bot token
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# In-memory user data (use a database for production)
users = {}
games = {}  # Track ongoing games

# Constants for user state
MAIN_MENU = 'main_menu'
DEPOSIT = 'deposit'
WITHDRAW = 'withdraw'
DICE_GAME = 'dice_game'
CHOOSE_OPPONENT = 'choose_opponent'

# Define your test user ID and balance here
TEST_USER_ID = 6764153691
TEST_USER_BALANCE = 2635  # Amount in dollars

# Initialize the user with a specific balance for testing
users[TEST_USER_ID] = {"balance": TEST_USER_BALANCE, "state": MAIN_MENU, "prev_state": MAIN_MENU}

# Your wallet address
WALLET_ADDRESS = "0x3A035f8B7215fEb5c68c74665Fbaf9255681A8FB"

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_first_name = update.message.from_user.first_name  # Get the user's first name

    if user_id not in users:
        users[user_id] = {"balance": 0, "state": MAIN_MENU, "prev_state": MAIN_MENU}  # Initialize user with a balance of 0 dollars

    keyboard = [
        [InlineKeyboardButton("💰 Check Balance", callback_data='balance')],
        [InlineKeyboardButton("🎲 Play Dice Game", callback_data='dice')],
        [InlineKeyboardButton("💸 Deposit Crypto", callback_data='deposit')],
        [InlineKeyboardButton("📤 Withdraw Crypto", callback_data='withdraw')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Personalized greeting message
    await update.message.reply_text(
        f'*Welcome to the Casino Bot, {user_first_name}!*\n\n_What would you like to do?_', 
        reply_markup=reply_markup, 
        parse_mode="Markdown"
    )

# Callback handler for button presses
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id

    await query.answer()

    # Handle user state and callback data
    if query.data == 'balance':
        users[user_id]["prev_state"] = users[user_id]["state"]
        users[user_id]["state"] = 'balance'
        balance = users.get(user_id, {}).get("balance", 0)
        keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=f"💰 *Your current balance is:* _${balance}_", reply_markup=reply_markup, parse_mode="Markdown")

    elif query.data == 'dice':
        users[user_id]["prev_state"] = users[user_id]["state"]
        users[user_id]["state"] = CHOOSE_OPPONENT
        keyboard = [
            [InlineKeyboardButton("🤖 Play with Bot", callback_data='play_with_bot')],
            [InlineKeyboardButton("👤 Play with Another User", callback_data='play_with_user')],
            [InlineKeyboardButton("🚫 Cancel", callback_data='cancel')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="🎲 *How would you like to play?*", reply_markup=reply_markup, parse_mode="Markdown")

    elif query.data == 'deposit':
        users[user_id]["prev_state"] = users[user_id]["state"]
        users[user_id]["state"] = DEPOSIT
        keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=f"💸 *Please send the amount you want to deposit.*\n_Your deposit address is:_ `{WALLET_ADDRESS}`", reply_markup=reply_markup, parse_mode="Markdown")
    
    elif query.data == 'withdraw':
        users[user_id]["prev_state"] = users[user_id]["state"]
        users[user_id]["state"] = WITHDRAW
        keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="📤 *Please enter the amount you want to withdraw:*", reply_markup=reply_markup, parse_mode="Markdown")

    elif query.data == 'play_with_bot':
        users[user_id]["prev_state"] = CHOOSE_OPPONENT
        users[user_id]["state"] = DICE_GAME
        await query.edit_message_text(text="🎲 *Please enter the amount you want to bet:*", parse_mode="Markdown")

    elif query.data == 'play_with_user':
        # Handle playing with another user (implementation needed)
        await query.edit_message_text(text="👤 *Playing with another user is not yet implemented.*", parse_mode="Markdown")

    elif query.data == 'cancel':
        users[user_id]["state"] = MAIN_MENU
        await start(update, context)  # Go back to the main menu

    elif query.data == 'back':
        prev_state = users[user_id].get("prev_state", MAIN_MENU)
        if prev_state == MAIN_MENU:
            await start(update, context)  # Go back to the main menu
        else:
            users[user_id]["state"] = prev_state
            # Redraw the previous state message
            if prev_state == DEPOSIT:
                keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data='back')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(text=f"💸 *Please send the amount you want to deposit.*\n_Your deposit address is:_ `{WALLET_ADDRESS}`", reply_markup=reply_markup, parse_mode="Markdown")
            elif prev_state == WITHDRAW:
                keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data='back')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(text="📤 *Please enter the amount you want to withdraw:*", reply_markup=reply_markup, parse_mode="Markdown")
            elif prev_state == CHOOSE_OPPONENT:
                keyboard = [
                    [InlineKeyboardButton("🤖 Play with Bot", callback_data='play_with_bot')],
                    [InlineKeyboardButton("👤 Play with Another User", callback_data='play_with_user')],
                    [InlineKeyboardButton("🚫 Cancel", callback_data='cancel')]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(text="🎲 *How would you like to play?*", reply_markup=reply_markup, parse_mode="Markdown")
            elif prev_state == 'balance':
                await button(update, context)  # Re-show balance
            else:
                await start(update, context)  # Default to main menu if previous state is unknown

# Handler for processing bets, deposits, and withdrawals
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_message = update.message.text

    if user_id not in users:
        await update.message.reply_text("Please start the bot with /start")
        return

    user_state = users[user_id].get("state", MAIN_MENU)

    if user_state == DEPOSIT:
        try:
            deposit_amount = float(user_message)
            if deposit_amount <= 0:
                await update.message.reply_text("❗️ Deposit amount must be greater than zero.")
                return
            users[user_id]["balance"] += deposit_amount
            users[user_id]["state"] = MAIN_MENU
            await update.message.reply_text(f"💸 *You have successfully deposited ${deposit_amount}.*\n💰 *Your new balance is ${users[user_id]['balance']}.*")
        except ValueError:
            await update.message.reply_text("❗️ Please enter a valid amount.")
        return

    if user_state == WITHDRAW:
        try:
            withdraw_amount = float(user_message)
            if withdraw_amount <= 0:
                await update.message.reply_text("❗️ Withdrawal amount must be greater than zero.")
                return
            if withdraw_amount > users[user_id]["balance"]:
                await update.message.reply_text("🚫 You don't have enough balance to withdraw this amount.")
                return
            users[user_id]["balance"] -= withdraw_amount
            users[user_id]["state"] = MAIN_MENU
            await update.message.reply_text(f"📤 *You have successfully withdrawn ${withdraw_amount}.*\n💰 *Your new balance is ${users[user_id]['balance']}.*")
        except ValueError:
            await update.message.reply_text("❗️ Please enter a valid amount.")
        return

    if user_state == DICE_GAME:
        if not user_message.isdigit():
            await update.message.reply_text("❗️ Please enter a valid number for your bet.")
            return

        bet_amount = int(user_message)

        if bet_amount <= 0:
            await update.message.reply_text("❗️ Bet amount must be greater than zero.")
            return

        if bet_amount > users[user_id]["balance"]:
            await update.message.reply_text("🚫 You don't have enough balance to place this bet.")
            return

        # Send the dice animation
        dice_message = await update.message.reply_dice()  # Sends animated dice

        # Simulate dice roll (1-6)
        roll = random.randint(1, 6)

        # Wait for the dice animation to complete
        await asyncio.sleep(2)

        if roll > 3:
            users[user_id]["balance"] += bet_amount  # Win: double the bet amount
            result = f"🎉 *You rolled a {roll}!*\n_You win ${bet_amount}!_\n💰 *Your new balance is ${users[user_id]['balance']}.*"
        else:
            users[user_id]["balance"] -= bet_amount  # Lose: subtract the bet amount
            result = f"😢 *You rolled a {roll}.*\n_You lose ${bet_amount}._\n💰 *Your new balance is ${users[user_id]['balance']}.*"

        await dice_message.edit_text(result, parse_mode="Markdown")
        users[user_id]["state"] = MAIN_MENU

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
