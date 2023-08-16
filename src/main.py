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
    global buttons
    global steps
    mess = 'Твой ход'
    keyboard = types.ReplyKeyboardMarkup()

    # крестик   
    buttons[buttons.index(message.text)] = '\u274C'
    steps.pop(steps.index(message.text))

    if not win(buttons=buttons):
        if steps:
            bot_step = random.choice(steps)
            # нолик
            buttons[buttons.index(bot_step)] = '\u2B55'
            steps.remove(bot_step)
            if win(buttons=buttons):
                mess='Я выиграл\nКонец игры'
                steps = []
        else:
            mess = 'Ничья\nКонец игры'
    else:
        mess = 'Ты выиграл\nКонец игры'
        steps = []

    keyboard.add(*buttons)
    await message.answer(mess, reply_markup=keyboard)


#@dp.message_handler()
async def echo(message: types.Message):
    # old style:
    # await bot.send_message(message.chat.id, message.text)
    await message.answer(message.text)

def win(buttons: buttons):
    print(buttons)
    if buttons[0] == buttons[1] and buttons[0] == buttons[2]:
        return True
    if buttons[3] == buttons[4] and buttons[3] == buttons[5]:
        return True
    if buttons[6] == buttons[7] and buttons[6] == buttons[8]:
        return True
    if buttons[0] == buttons[3] and buttons[0] == buttons[6]:
        return True
    if buttons[1] == buttons[4] and buttons[1] == buttons[7]:
        return True
    if buttons[2] == buttons[5] and buttons[2] == buttons[8]:
        return True
    if buttons[0] == buttons[4] and buttons[0] == buttons[8]:
        return True
    if buttons[2] == buttons[4] and buttons[2] == buttons[6]:
        return True
    return False


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
