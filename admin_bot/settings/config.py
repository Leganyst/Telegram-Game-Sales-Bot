# Здесь бот для админов, который будет настраивать товары 

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage


PROVIDER_TOKEN = 'your payment provider token'
QIWI_PAY_TRANSFER_LINK = 'your link'

# Инициализация бота
bot_admin = Bot(token='your bot token')
storage = MemoryStorage()
dp_admin = Dispatcher(bot_admin, storage=storage)






