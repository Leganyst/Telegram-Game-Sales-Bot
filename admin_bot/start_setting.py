from aiogram import types
from aiogram.dispatcher import FSMContext

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
    user_mention = f'<a href="https://t.me/legannyst">Марк Клавишин</a>'
    response = (
        f"Привет, администратор!\n\n"
        f"Этот бот предназначен для настройки маркета игр.\n"
        f"Вы можете создавать карточки товаров с картинками, описаниями, ценами и жанрами игр.\n\n"
        f"Создатель бота - {user_mention}\n"
        f"По всем вопросам обращайтесь к нему.\n\n"
        f"Бот создан в рамках учебного курса университета Иннополис."
    )
    await message.reply(response, parse_mode=types.ParseMode.HTML)

@dp_admin.message_handler(WhitelistFilter(white_list), commands=['settings'])
async def settings_command(message: types.Message):
    genres_table = GenresTable()
    if genres_table.has_genres():
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        edit_button = types.InlineKeyboardButton("Редактировать", callback_data="edit")
        delete_button = types.InlineKeyboardButton("Удалить", callback_data="delete")
        add_button = types.InlineKeyboardButton("Добавить", callback_data="add")
        create_genre = types.InlineKeyboardButton('Создать жанр', callback_data='create_genre')
        keyboard.add(edit_button, delete_button, add_button, create_genre)
    else:
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        create_genre = types.InlineKeyboardButton('Создать жанр', callback_data='create_genre')
        keyboard.add(create_genre)

    await message.reply("Выберите вариант развития событий:", reply_markup=keyboard)




