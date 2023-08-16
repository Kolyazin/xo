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

# загружаю токен в переменные окружения из файла .env
load_dotenv()

# Bot token can be obtained via https://t.me/BotFather
API_TOKEN = getenv("BOT_TOKEN")

# если токен не подгрузился, завершаю работу программы
if not API_TOKEN:
    exit("Error: no token provided")

# включаю логирование
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
# создаю хранилище, где будут храниться счет, состояние игрового поля
storage = MemoryStorage()
# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher(bot, storage=storage)

class XOStates(StatesGroup):
    # для ожидания следующего хода
    wait_next_step = State()

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    # This handler will be called when user sends `/start` or `/help` command
    await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram.")

@dp.message_handler(commands='xo')
async def show_time(message: types.Message, state: FSMContext):
    # получаю данные из хранилища
    data = await state.get_data()
    # инициализация поля и доступных ходов
    data['buttons'] = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
    data['steps'] = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
    # получаю или инициализирую при отсутсвии данных поля с количеством выигрышей пользователя и бота
    users_win = data.setdefault('users_win', 0)
    bots_win = data.setdefault('bots_win', 0)
    # сохраняю все в хранилище обратно
    await state.update_data(data)
    # инициализирую клавиатуру, по умолчанию поле rows = 3
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.add(*data['buttons'])
    await message.answer(f'Крестики-нолики\nПривет, {message.from_user.first_name}\nСчет: {message.from_user.first_name} {users_win}:{bots_win} bot\nТвой ход', reply_markup=keyboard)
    await XOStates.wait_next_step.set()

@dp.message_handler(state=XOStates.wait_next_step)
async def play(message: types.Message, state: FSMContext):
    mess = 'Твой ход'
    keyboard = types.ReplyKeyboardMarkup()

    data = await state.get_data()
    # ставлю крестик на кнопку, которую нажал пользователь, определяется по тексту на кнопке  
    data['buttons'][data['buttons'].index(message.text)] = '\u274C'
    # удаляю эту кнопку из доступных для нажатия
    data['steps'].pop(data['steps'].index(message.text))

    # проверяю не появилась ли выигрышная комбинация
    if not win(buttons=data['buttons']):
        # если не появилась, то ходит бот, проверяю есть ли доступные ходы
        if data['steps']:
            # если есть, выбираю из доступных случайный
            bot_step = random.choice(data['steps'])
            # ставлю нолик на выбранную кнопку
            data['buttons'][data['buttons'].index(bot_step)] = '\u2B55'
            # удаляю эту кнопку из доступных для нажатия
            data['steps'].remove(bot_step)
            # проверяю не появилась ли выигрышная комбинация
            if win(buttons=data['buttons']):
                # если появилась, то бот выиграл, увеличиваю количество побед бота и сбрасываю условие для хэндлера
                mess='Я выиграл\nКонец игры'
                data['bots_win'] = data.get('bots_win') + 1
                await state.reset_state()
        else:
            # если пользователь не выиграл и доступных шагов нет, то ничья, сбрасываю условие для хэндлера
            mess = 'Ничья\nКонец игры'
            await state.reset_state()
    else:
        # пользователь выиграл, увеличиваю количество побед пользователя  и сбрасываю условие для хэндлера
        mess = 'Ты выиграл\nКонец игры'
        data['users_win'] = data.get('users_win') + 1
        await state.reset_state()

    # обновляю данные в хранилище
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
