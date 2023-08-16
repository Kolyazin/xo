import logging
import random
from dotenv import load_dotenv
from os import getenv
from sys import exit

from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils import executor
from aiogram.dispatcher.filters import Text

load_dotenv()
# Bot token can be obtained via https://t.me/BotFather
API_TOKEN = getenv("BOT_TOKEN")
if not API_TOKEN:
    exit("Error: no token provided")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram.")

buttons = []
steps = []
keyboard = types.ReplyKeyboardMarkup()

@dp.message_handler(commands='xo')
async def kbd(message: types.Message):
#    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    global buttons
    global steps
    buttons = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
    steps = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.add(*buttons)
    await message.answer("Крестики-нолики", reply_markup=keyboard)

@dp.message_handler(lambda message: message.text in steps)
async def one(message: types.Message):
    global steps
    mess = 'Твой ход'
    print(message)
    keyboard = types.ReplyKeyboardMarkup()

    print(buttons)
    print(steps)
    buttons[buttons.index(message.text)] = '\u274C'
    print(message.text)
    steps.pop(steps.index(message.text))

    if steps:
        bot_step = random.choice(steps)
        buttons[buttons.index(bot_step)] = '\u2B55'
        steps.remove(bot_step)
    else:
        mess = 'Конец игры'
    keyboard.add(*buttons)
    await message.answer(mess, reply_markup=keyboard)


#@dp.message_handler()
async def echo(message: types.Message):
    # old style:
    # await bot.send_message(message.chat.id, message.text)
    await message.answer(message.text)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
