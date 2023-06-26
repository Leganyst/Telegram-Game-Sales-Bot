# Здесь бот для админов, который будет настраивать товары 

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage


PROVIDER_TOKEN = '381764678:TEST:58846'
QIWI_PAY_TRANSFER_LINK = 'https://my.qiwi.com/Oleg-SEp8uS3mc6?noCache=true'

# Инициализация бота
bot_admin = Bot(token='6186960397:AAH0AcKJfnQ0XCXbqo13-6ut7a0-L-z1Ovo')
storage = MemoryStorage()
dp_admin = Dispatcher(bot_admin, storage=storage)






