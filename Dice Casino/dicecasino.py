import os
import asyncio
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Dice
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import random

# Load environment variables from .env file
load_dotenv()

# Telegram bot token
TELEGRAM_BOT_TOKEN = os.getenv('7000894405:AAFR_Yi4ljLldytaNPHB4p88NkU2-xLFXeE')

# In-memory user data (use a database for production)
users = {}
games = {}  # Track ongoing games

# Constants for user state
MAIN_MENU = 'main_menu'
DEPOSIT = 'deposit'
WITHDRAW = 'withdraw'
DICE_GAME = 'dice_game'
CHOOSE_OPPONENT = 'choose_opponent'
BET_AMOUNT = 'bet_amount'
ROUND_SELECTION = 'round_selection'

# Define your test user ID and balance here
TEST_USER_ID = 6764153691
TEST_USER_BALANCE = 50000  # Amount in dollars

# Initialize the user with a specific balance for testing
users[TEST_USER_ID] = {"balance": TEST_USER_BALANCE, "state": MAIN_MENU}

# Your wallet address
WALLET_ADDRESS = "0x3A035f8B7215fEb5c68c74665Fbaf9255681A8FB"

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_first_name = update.message.from_user.first_name  # Get the user's first name

    if user_id not in users:
        users[user_id] = {"balance": 0, "state": MAIN_MENU}  # Initialize user with a balance of 0 dollars

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

    if query.data == 'balance':
        balance = users.get(user_id, {}).get("balance", 0)
        keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=f"💰 *Your current balance is:* _${balance}_", reply_markup=reply_markup, parse_mode="Markdown")

    elif query.data == 'dice':
        users[user_id]["state"] = BET_AMOUNT
        await query.edit_message_text(text="🎲 *How much would you like to bet?* (Enter the amount)", parse_mode="Markdown")

    elif query.data == 'deposit':
        users[user_id]["state"] = DEPOSIT
        keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=f"💸 *Please send the amount you want to deposit.*\n_Your deposit address is:_ `{WALLET_ADDRESS}`", reply_markup=reply_markup, parse_mode="Markdown")
    
    elif query.data == 'withdraw':
        users[user_id]["state"] = WITHDRAW
        keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="📤 *Please enter the amount you want to withdraw:*", reply_markup=reply_markup, parse_mode="Markdown")

    elif query.data == 'play_with_bot':
        users[user_id]["state"] = ROUND_SELECTION
        await query.edit_message_text(text="🎲 *How many rounds would you like to play? (Max 3)*", parse_mode="Markdown")

    elif query.data == 'play_with_user':
        # Handle playing with another user (implementation needed)
        await query.edit_message_text(text="👤 *Playing with another user is not yet implemented.*", parse_mode="Markdown")

    elif query.data == 'cancel':
        users[user_id]["state"] = MAIN_MENU
        await start(update, context)  # Go back to the main menu

    elif query.data == 'back':
        previous_state = users[user_id]["state"]
        if previous_state == DICE_GAME:
            users[user_id]["state"] = CHOOSE_OPPONENT
            await button(update, context)  # Re-show the choice of opponent
        else:
            users[user_id]["state"] = MAIN_MENU
            await start(update, context)  # Go back to the main menu

# Handler for processing bets, deposits, and withdrawals
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_message = update.message.text

    if user_id not in users:
        await update.message.reply_text("Please start the bot with /start")
        return

    user_state = users[user_id].get("state", MAIN_MENU)

    if user_state == BET_AMOUNT:
        try:
            bet_amount = float(user_message)
            if bet_amount <= 0:
                await update.message.reply_text("❗️ Bet amount must be greater than zero.")
                return
            if bet_amount > users[user_id]["balance"]:
                await update.message.reply_text("🚫 You don't have enough balance to place this bet.")
                return

            users[user_id]["state"] = CHOOSE_OPPONENT
            games[user_id] = {"bet_amount": bet_amount, "rounds": 0, "user_score": 0, "bot_score": 0}

            keyboard = [
                [InlineKeyboardButton("🤖 Play with Bot", callback_data='play_with_bot')],
                [InlineKeyboardButton("👤 Play with Another User", callback_data='play_with_user')],
                [InlineKeyboardButton("🚫 Cancel", callback_data='cancel')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(text="🎲 *How would you like to play?*", reply_markup=reply_markup, parse_mode="Markdown")

        except ValueError:
            await update.message.reply_text("❗️ Please enter a valid amount.")
        return

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

    if user_state == ROUND_SELECTION:
        try:
            rounds = int(user_message)
            if rounds <= 0 or rounds > 3:
                await update.message.reply_text("❗️ Number of rounds must be between 1 and 3.")
                return
            games[user_id]["rounds"] = rounds
            users[user_id]["state"] = DICE_GAME
            await update.message.reply_text("🎲 *You will roll first. Send /roll to roll the dice.*", parse_mode="Markdown")
        except ValueError:
            await update.message.reply_text("❗️ Please enter a valid number of rounds.")
        return

    if user_state == DICE_GAME:
        if user_message == '/roll':
            if user_id not in games or games[user_id]["rounds"] <= 0:
                await update.message.reply_text("❗️ Please start a game first by choosing the number of rounds.")
                return

            # User rolls the dice
            user_roll = random.randint(1, 6)
            games[user_id]["user_score"] += user_roll

            # Bot rolls the dice
            bot_roll = random.randint(1, 6)
            games[user_id]["bot_score"] += bot_roll

            # Calculate the results
            rounds_left = games[user_id]["rounds"] - 1
            games[user_id]["rounds"] = rounds_left

            # Send the dice roll animation
            dice_emoji = Dice(emoji="🎲")
            await update.message.reply_dice(emoji=dice_emoji.emoji)

            if rounds_left > 0:
                await update.message.reply_text(f"🎲 *You rolled:* {user_roll}\n🤖 *Bot rolled:* {bot_roll}\n\n*Rounds left:* {rounds_left}\n\nSend /roll again to continue.")
            else:
                user_score = games[user_id]["user_score"]
                bot_score = games[user_id]["bot_score"]

                if user_score > bot_score:
                    result_text = f"🎉 *Congratulations!* You win with a score of {user_score} against the bot's {bot_score}."
                elif user_score < bot_score:
                    result_text = f"😢 *You lost.* The bot wins with a score of {bot_score} against your {user_score}."
                else:
                    result_text = f"🤝 *It's a tie!* Both you and the bot scored {user_score}."

                del games[user_id]  # End the game

                await update.message.reply_text(result_text, parse_mode="Markdown")
        return

# Main function to start the bot
async def main() -> None:
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button))

    # Run the bot with the proper event loop management
    loop = asyncio.get_event_loop()
    try:
        await application.run_polling()
    finally:
        # Ensure the event loop is properly closed
        loop.close()

if __name__ == '__main__':
    asyncio.run(main())
