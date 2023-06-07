
from aiogram import types

from admin_bot.settings.config import dp_admin, bot_admin

@dp_admin.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    user = message.from_user
    username = user.first_name 

    # Формируем текст приветствия с гиперссылкой на ваш телеграм
    bot_creator = "Марк Клавишин"
    bot_creator_telegram = "@legannyst"
    greeting_text = f"Привет, {username}!\n"
    greeting_text += f"Я бот для продажи игр. Меня сделал [{bot_creator}]({bot_creator_telegram}).\n"
    greeting_text += "По всем вопросам нужно обращаться к нему.\n"
    greeting_text += "Для того, чтобы купить игру, введи команду /buy."

    # Создаем сообщение с форматированным текстом и гиперссылкой
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text=bot_creator, url=f"https://t.me/{bot_creator_telegram}"))

    await bot_admin.send_message(chat_id=message.chat.id, text=greeting_text, parse_mode="Markdown", reply_markup=markup)
