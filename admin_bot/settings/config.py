# Здесь бот для админов, который будет настраивать товары 

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage


PROVIDER_TOKEN = 'payment_provider_token'

# Инициализация бота
bot_admin = Bot(token='bot_token')
storage = MemoryStorage()
dp_admin = Dispatcher(bot_admin, storage=storage)






