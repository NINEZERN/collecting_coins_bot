from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove


b1 = KeyboardButton("Все монеты 💰")
b2 = KeyboardButton("Поиск монеты 🪙")
b3 = KeyboardButton("Добавить монету 💲")

back = KeyboardButton("⤴ Назад")
menu = ReplyKeyboardMarkup(resize_keyboard=True).add(b2).add(b1).insert(b3)
back2menu = ReplyKeyboardMarkup(resize_keyboard=True).add(back)