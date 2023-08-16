import logging
import random
from dotenv import load_dotenv
from os import getenv
from sys import exit

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.storage import FSMContext

load_dotenv()
# Bot token can be obtained via https://t.me/BotFather
API_TOKEN = getenv("BOT_TOKEN")
if not API_TOKEN:
    exit("Error: no token provided")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher(bot, storage=storage)

class XOStates(StatesGroup):
    wait_next_step = State()

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    # This handler will be called when user sends `/start` or `/help` command
    await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram.")

@dp.message_handler(commands='xo')
async def show_time(message: types.Message, state: FSMContext):
    data = await state.get_data()
    data['buttons'] = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
    data['steps'] = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
    await state.update_data(data)
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.add(*data['buttons'])
    await message.answer(f'Крестики-нолики\nПривет, {message.from_user.first_name}\nТвой ход', reply_markup=keyboard)
    await XOStates.wait_next_step.set()

@dp.message_handler(state=XOStates.wait_next_step)
async def play(message: types.Message, state: FSMContext):
    mess = 'Твой ход'
    keyboard = types.ReplyKeyboardMarkup()

    data = await state.get_data()
    # крестик   
    data['buttons'][data['buttons'].index(message.text)] = '\u274C'
    data['steps'].pop(data['steps'].index(message.text))

    if not win(buttons=data['buttons']):
        if data['steps']:
            bot_step = random.choice(data['steps'])
            # нолик
            data['buttons'][data['buttons'].index(bot_step)] = '\u2B55'
            data['steps'].remove(bot_step)
            if win(buttons=data['buttons']):
                mess='Я выиграл\nКонец игры'
                await state.reset_state()
        else:
            mess = 'Ничья\nКонец игры'
            await state.reset_state()
    else:
        mess = 'Ты выиграл\nКонец игры'
        await state.reset_state()

    await state.update_data(data)
    keyboard.add(*data['buttons'])
    await message.answer(mess, reply_markup=keyboard)


#@dp.message_handler()
async def echo(message: types.Message):
    # old style:
    # await bot.send_message(message.chat.id, message.text)
    await message.answer(message.text)

def win(buttons: []):
#    print(buttons)
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
