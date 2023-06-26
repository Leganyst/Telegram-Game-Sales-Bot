from aiogram import types
from aiogram.dispatcher import FSMContext

from database.users_table_operations import UsersTable
from database.genres_table_operations import GenresTable
from .states import AddCardState
from .settings.config import dp_admin, bot_admin
from .filters import WhitelistFilter
from whitelist import white_list

# Здесь мы устанавливаем run_task=10, чтобы он запускался первым
@dp_admin.message_handler(commands=["cancel"], run_task=10, state="*")
async def reset_handler(message: types.Message, state: FSMContext):
    # Здесь мы сбрасываем все состояния и данные пользователя
    await state.finish()
    # Здесь мы отправляем сообщение пользователю
    await message.answer("Вы вышли из текущего режима.")


@dp_admin.message_handler(WhitelistFilter(white_list), commands=['start'])
async def start_command(message: types.Message):
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


    user_mention = f'<a href="https://t.me/legannyst">Марк Клавишин</a>'
    response = (
        f"Привет, администратор! 👋\n\n"
        f"Этот бот предназначен для настройки маркета игр. 🎮🛒\n"
        f"Вы можете создавать карточки товаров с картинками, описаниями, ценами и жанрами игр. 💡✨\n\n"
        f"Создатель бота - {user_mention}\n"
        f"По всем вопросам обращайтесь к нему. 🙋‍♂️📞\n\n"
        f"Бот создан в рамках учебного курса университета Иннополис. 🎓🏛️\n\n"
        f"Для начала настройки используйте команду /settings. ⚙️🔧\n\n"
        f"Вы можете просмотреть этап покупки от лица пользователя введя команду /buy. 🛒💸"
    )
    await message.reply(response, parse_mode=types.ParseMode.HTML)


@dp_admin.message_handler(WhitelistFilter(white_list), commands=['settings'])
async def settings_command(message: types.Message):
    genres_table = GenresTable()
    if genres_table.has_genres():
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        edit_button = types.InlineKeyboardButton("Редактировать карточку игры", callback_data="edit")
        delete_button = types.InlineKeyboardButton("Удалить карточку игры", callback_data="delete")
        add_button = types.InlineKeyboardButton("Добавить карточку игры", callback_data="add")
        create_genre = types.InlineKeyboardButton('Создать жанр', callback_data='create_genre')
        keyboard.add(edit_button, delete_button, add_button, create_genre)
        await message.reply("Выберите действие:", reply_markup=keyboard)
    else:
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        create_genre = types.InlineKeyboardButton('Создать жанр', callback_data='create_genre')
        keyboard.add(create_genre)
        await message.reply("В настоящее время нет созданных жанров для создания игры. Вам необходимо создать новый жанр:", reply_markup=keyboard)
