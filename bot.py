from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ParseMode
from aiogram.dispatcher.filters import Text
from aiogram.utils.markdown import hbold
import texts
import kb
from config import BOT_TOKEN
from db import BotDB
from tabulate import tabulate
import time

BotDB = BotDB('coin_collection.db')


storage = MemoryStorage()

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)

# State Machine
class Coin(StatesGroup):
    name = State()
    description = State()
    photo = State()

@dp.message_handler(Text(equals="⤴ Назад", ignore_case=True))
async def back(message: types.Message):
    await message.reply("Вы в меню", reply_markup=kb.menu)

# Exit machine state
@dp.message_handler(state='*', commands='⤴ Назад')
@dp.message_handler(Text(equals="⤴ Назад", ignore_case=True), state='*')
async def cancel_handle(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('Вы в меню', reply_markup=kb.menu)



### COMMANDS TO ADD COIN ###

# Command to add coin
@dp.message_handler(Text(equals="Добавить монету 💲"))
async def add_coin(message: types.Message):
    await Coin.name.set()
    await message.answer('Напишите название', reply_markup=kb.back2menu)


# Load name
@dp.message_handler(state=Coin.name)
async def load_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await Coin.next()
    await message.reply('Напишите описание')

# Load description
@dp.message_handler(state=Coin.description)
async def load_description(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = message.text
    await Coin.next()
    await message.reply('Отправьте фото')




# Load photo

@dp.message_handler(content_types=['photo'] ,state=Coin.photo)
async def load_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['photo'] = message.photo[0].file_id
    
    async with state.proxy() as data:
        BotDB.add_coin(message.from_user.id, data['name'], data['description'], data['photo'])
    await message.reply("✔️ Монета добавлена")
    await state.finish()


### COMMANDS TO GET COINS  ###

class CoinName(StatesGroup):
    name = State()

# Get coins by name
@dp.message_handler(Text(equals="Поиск монеты 🪙"))
async def get_coins_by_name(message: types.Message):
    await CoinName.name.set()
    await message.answer('Напишите название', reply_markup=kb.back2menu)

# Load name
@dp.message_handler(state=CoinName.name)
async def load_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    
    async with state.proxy() as data:
        coins = BotDB.get_coins(message.from_user.id, name=data["name"])
        
        if not coins:
            await message.answer("Похоже что у вас совсем нет монет :(")
            return
        names = [coin[1] for coin in coins]
        if not (data['name'] in names):
            await message.reply("Такой монеты нет в списке")
            await state.finish()
            return

        for coin in coins:
            card = f'{hbold("Название: ")}{coin[1]}\n' \
                f'{hbold("Описание: ")}{coin[2]}'
            await message.bot.send_photo(message.from_user.id, coin[3], card, reply_markup=kb.menu)
    await state.finish()
    


# Get all coins
@dp.message_handler(Text(equals="Все монеты 💰"))
async def get_only_coin_names(message: types.Message):
    data = BotDB.get_coin_names(message.from_user.id)
    if not data:
        await message.answer("Похоже что у вас совсем нет монет :( ")
        return
    # table headers
    buttons = []
    # create two inline buttons
    
    for (coin, count) in data[:5]:
        button = types.InlineKeyboardButton(text=f"{coin} - {count}", callback_data=f"{coin[1]}")
        buttons.append(button)
        

    # create an inline keyboard with the two buttons
    keyboard = types.InlineKeyboardMarkup()
    for btn in buttons:
        keyboard.add(btn)

    # send the table to the user
    await message.answer("Монеты | Кол-во", reply_markup=keyboard)



# Start
@dp.message_handler(commands=['start', 'help'])
async def start(message: types.Message):
    if (not BotDB.user_exists(message.from_user.id)):
        BotDB.add_user(message.from_user.id)
    await message.answer(texts.greet.format(name=message.from_user.full_name), reply_markup=kb.menu)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)