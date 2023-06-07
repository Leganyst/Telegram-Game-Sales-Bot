from aiogram import types
from aiogram.types import Message
from aiogram.dispatcher import FSMContext

from database.genres_table_operations import GenresTable
from .states import AddGenreState
from .settings.config import dp_admin, bot_admin

import sqlite3

# Обработчик инлайн-кнопки "Создать жанр"
@dp_admin.callback_query_handler(lambda query: query.data == 'create_genre')
async def create_genre_handler(query: types.CallbackQuery, state: FSMContext):
    await query.answer()
    # Удаление предыдущего сообщения
    await bot_admin.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
    await bot_admin.send_message(chat_id=query.message.chat.id, text="Введите название жанра:")
    # Устанавливаем состояние для ожидания ввода названия жанра
    await AddGenreState.waiting_for_genre_name.set()


# Обработчик состояния ожидания ввода названия жанра
@dp_admin.message_handler(state=AddGenreState.waiting_for_genre_name)
async def add_genre_handler(message: Message, state: FSMContext):
    genre_name = message.text
    genres_table = GenresTable()
    try:
        genres_table.add_genre(genre_name)
        await message.answer(f"Жанр '{genre_name}' успешно добавлен.")
    except sqlite3.Error as e:
        await message.answer("Ошибка при добавлении жанра. Вероятно, он уже существует.")
        print(f'Ошибка добавления жанра: {e}')
    finally:
        await state.finish()
