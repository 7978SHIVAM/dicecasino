import os
import asyncio
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Dice
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import random
import sqlite3
from typing import Optional

# Load environment variables from .env file
load_dotenv()

# Constants
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
DATABASE_FILE = 'users.db'
WALLET_ADDRESS = os.getenv('WALLET_ADDRESS', "0x3A035f8B7215fEb5c68c74665Fbaf9255681A8FB")

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants for user state
MAIN_MENU = 'main_menu'
DEPOSIT = 'deposit'
WITHDRAW = 'withdraw'
DICE_GAME = 'dice_game'
CHOOSE_OPPONENT = 'choose_opponent'

class User:
    def __init__(self, user_id: int, balance: float, state: str, prev_state: Optional[str] = MAIN_MENU):
        self.user_id = user_id
        self.balance = balance
        self.state = state
        self.prev_state = prev_state

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'balance': self.balance,
            'state': self.state,
            'prev_state': self.prev_state
        }

class Database:
    def __init__(self, db_file: str):
        self.conn = sqlite3.connect(db_file)
        self.create_table()

    def create_table(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    balance REAL NOT NULL,
                    state TEXT NOT NULL,
                    prev_state TEXT
                )
            ''')

    def get_user(self, user_id: int) -> Optional[User]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        if row:
            return User(user_id=row[0], balance=row[1], state=row[2], prev_state=row[3])
        return None

    def save_user(self, user: User):
        with self.conn:
            self.conn.execute('''
                INSERT OR REPLACE INTO users (user_id, balance, state, prev_state)
                VALUES (?, ?, ?, ?)
            ''', (user.user_id, user.balance, user.state, user.prev_state))

database = Database(DATABASE_FILE)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_first_name = update.message.from_user.first_name

    user = database.get_user(user_id)
    if not user:
        user = User(user_id=user_id, balance=0.0, state=MAIN_MENU)
        database.save_user(user)

    keyboard = [
        [InlineKeyboardButton("💰 Check Balance", callback_data='balance')],
        [InlineKeyboardButton("🎲 Play Dice Game", callback_data='dice')],
        [InlineKeyboardButton("💸 Deposit Crypto", callback_data='deposit')],
        [InlineKeyboardButton("📤 Withdraw Crypto", callback_data='withdraw')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f'*Welcome to the Casino Bot, {user_first_name}!*\n\n_What would you like to do?_', 
        reply_markup=reply_markup, 
        parse_mode="Markdown"
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id

    await query.answer()

    user = database.get_user(user_id)
    if not user:
        await query.edit_message_text("User data not found.")
        return

    if query.data == 'balance':
        user.prev_state = user.state
        user.state = 'balance'
        database.save_user(user)
        balance = user.balance
        keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=f"💰 *Your current balance is:* _${balance}_", reply_markup=reply_markup, parse_mode="Markdown")

    elif query.data == 'dice':
        user.prev_state = user.state
        user.state = CHOOSE_OPPONENT
        database.save_user(user)
        keyboard = [
            [InlineKeyboardButton("🤖 Play with Bot", callback_data='play_with_bot')],
            [InlineKeyboardButton("👤 Play with Another User", callback_data='play_with_user')],
            [InlineKeyboardButton("🚫 Cancel", callback_data='cancel')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="🎲 *How would you like to play?*", reply_markup=reply_markup, parse_mode="Markdown")

    elif query.data == 'deposit':
        user.prev_state = user.state
        user.state = DEPOSIT
        database.save_user(user)
        keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=f"💸 *Please send the amount you want to deposit.*\n_Your deposit address is:_ `{WALLET_ADDRESS}`", reply_markup=reply_markup, parse_mode="Markdown")

    elif query.data == 'withdraw':
        user.prev_state = user.state
        user.state = WITHDRAW
        database.save_user(user)
        keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="📤 *Please enter the amount you want to withdraw:*", reply_markup=reply_markup, parse_mode="Markdown")

    elif query.data == 'play_with_bot':
        user.prev_state = CHOOSE_OPPONENT
        user.state = DICE_GAME
        database.save_user(user)
        await query.edit_message_text(text="🎲 *Please enter the amount you want to bet:*", parse_mode="Markdown")

    elif query.data == 'play_with_user':
        await query.edit_message_text(text="👤 *Playing with another user is not yet implemented.*", parse_mode="Markdown")

    elif query.data == 'cancel':
        user.state = MAIN_MENU
        database.save_user(user)
        await start(update, context)  # Go back to the main menu

    elif query.data == 'back':
        if user.prev_state == MAIN_MENU:
            await start(update, context)  # Go back to the main menu
        elif user.prev_state == 'balance':
            user.state = MAIN_MENU
            database.save_user(user)
            await start(update, context)  # Re-show balance
        elif user.prev_state == DEPOSIT:
            user.state = DEPOSIT
            database.save_user(user)
            keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data='back')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text=f"💸 *Please send the amount you want to deposit.*\n_Your deposit address is:_ `{WALLET_ADDRESS}`", reply_markup=reply_markup, parse_mode="Markdown")
        elif user.prev_state == WITHDRAW:
            user.state = WITHDRAW
            database.save_user(user)
            keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data='back')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text="📤 *Please enter the amount you want to withdraw:*", reply_markup=reply_markup, parse_mode="Markdown")
        elif user.prev_state == CHOOSE_OPPONENT:
            user.state = CHOOSE_OPPONENT
            database.save_user(user)
            keyboard = [
                [InlineKeyboardButton("🤖 Play with Bot", callback_data='play_with_bot')],
                [InlineKeyboardButton("👤 Play with Another User", callback_data='play_with_user')],
                [InlineKeyboardButton("🚫 Cancel", callback_data='cancel')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text="🎲 *How would you like to play?*", reply_markup=reply_markup, parse_mode="Markdown")
        else:
            user.state = MAIN_MENU
            database.save_user(user)
            await start(update, context)  # Default to main menu if previous state is unknown

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_message = update.message.text

    user = database.get_user(user_id)
    if not user:
        await update.message.reply_text("Please start the bot with /start")
        return

    if user.state == DEPOSIT:
        try:
            deposit_amount = float(user_message)
            if deposit_amount <= 0:
                await update.message.reply_text("❗️ Deposit amount must be greater than zero.")
                return
            user.balance += deposit_amount
            user.state = MAIN_MENU
            database.save_user(user)
            await update.message.reply_text(f"💸 *You have successfully deposited ${deposit_amount}.*\n💰 *Your new balance is ${user.balance}.*")
        except ValueError:
            await update.message.reply_text("❗️ Please enter a valid amount.")
        return

    if user.state == WITHDRAW:
        try:
            withdraw_amount = float(user_message)
            if withdraw_amount <= 0:
                await update.message.reply_text("❗️ Withdrawal amount must be greater than zero.")
                return
            if withdraw_amount > user.balance:
                await update.message.reply_text("🚫 You don't have enough balance to withdraw this amount.")
                return
            user.balance -= withdraw_amount
            user.state = MAIN_MENU
            database.save_user(user)
            await update.message.reply_text(f"📤 *You have successfully withdrawn ${withdraw_amount}.*\n💰 *Your new balance is ${user.balance}.*")
        except ValueError:
            await update.message.reply_text("❗️ Please enter a valid amount.")
        return

    if user.state == DICE_GAME:
        if not user_message.isdigit():
            await update.message.reply_text("❗️ Please enter a valid number for your bet.")
            return

        bet_amount = int(user_message)

        if bet_amount <= 0:
            await update.message.reply_text("❗️ Bet amount must be greater than zero.")
            return

        if bet_amount > user.balance:
            await update.message.reply_text("🚫 You don't have enough balance to place this bet.")
            return

        # Send the dice animation
        dice_message = await update.message.reply_dice()

        # Simulate dice roll (1-6)
        roll = random.randint(1, 6)

        # Wait for the dice animation to complete
        await asyncio.sleep(2)

        if roll > 3:
            user.balance += bet_amount
            result = f"🎉 *You rolled a {roll}!*\n_You win ${bet_amount}!_\n💰 *Your new balance is ${user.balance}.*"
        else:
            user.balance -= bet_amount
            result = f"😢 *You rolled a {roll}.*\n_You lose ${bet_amount}._\n💰 *Your new balance is ${user.balance}.*"

        await dice_message.edit_text(result, parse_mode="Markdown")
        user.state = MAIN_MENU
        database.save_user(user)

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
