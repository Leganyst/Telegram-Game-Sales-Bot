
from aiogram import types

from admin_bot.settings.config import dp_admin, bot_admin
from database.users_table_operations import UsersTable

@dp_admin.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    user = message.from_user
    user_id = user.id  # Идентификатор пользователя
    users_table = UsersTable()

    if not(users_table.get_user_by_id(user_id)):
        # Если пользователь не существует в бд, запишем его
        if user.username:
            user_link = f"https://t.me/{user.username}"  # Ссылка на аккаунт пользователя
        else:
            user_link = f"https://t.me/user?id={user_id}"  # Ссылка на аккаунт пользователя по user_id
        is_admin = False  # Значение is_admin (False по умолчанию)
            
        users_table.add_user(user_id=user_id, user_link=user_link, is_admin=is_admin)

    username = user.first_name 
    user_mention = f'<a href="https://t.me/legannyst">Марк Клавишин</a>'
    # Формируем текст приветствия с гиперссылкой на наш телеграм
    greeting_text = f"Привет, {username}! 😊\n"
    greeting_text += f"Я здесь, чтобы помочь тебе с покупкой игр. Создатель бота - {user_mention}. 🎮💪\n"
    greeting_text += "Если у тебя есть вопросы, не стесняйся обратиться ко мне. Я всегда готов помочь! 💬🤝\n"
    greeting_text += "Чтобы купить игру, просто введи команду /buy. 🛒💸"
    
    await bot_admin.send_message(chat_id=message.chat.id, text=greeting_text, parse_mode=types.ParseMode.HTML)
