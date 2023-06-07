from aiogram import types
from aiogram.dispatcher import FSMContext

from database.games_table_operations import GamesTable
from database.genres_table_operations import GenresTable
from .settings.config import dp_admin, bot_admin
from .states import DeleteGameState, EditGameState

@dp_admin.callback_query_handler(lambda query: query.data == 'delete')
async def delete_handler(query: types.CallbackQuery, state: FSMContext):
    await query.answer()
    games_table = GamesTable()
    games = games_table.select_rows(limit=5, offset=0) # получаем первые 5 игр

    offset = 0 # устанавливаем смещение на 0
    await state.update_data(offset=offset) # сохраняем смещение в state data

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for game in games:
        game_id = game[0]
        game_name = game[1]
        button = types.InlineKeyboardButton(game_name, callback_data=f"game_id:{game_id}")
        keyboard.add(button)

    # добавляем кнопку стрелки вправо
    next_button = types.InlineKeyboardButton("➡️", callback_data="next")
    # добавляем кнопку выхода
    cancel_button = types.InlineKeyboardButton("❌", callback_data="cancel")
    keyboard.row(cancel_button, next_button)

    await bot_admin.send_message(chat_id=query.message.chat.id, text="Выберите игру для удаления:", reply_markup=keyboard)

    # удаляем предыдущее сообщение
    await bot_admin.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)

    await state.set_state(DeleteGameState.ConfirmDelete)


@dp_admin.callback_query_handler(lambda query: query.data.startswith("game_id:"), state=DeleteGameState.ConfirmDelete)
async def confirm_delete_handler(query: types.CallbackQuery, state: FSMContext):
    await query.answer()

    game_id = query.data.split(":")[1]

    games_table = GamesTable()
    game = games_table.get_game_by_id(game_id)

    genres_table = GenresTable()
    genre_name = genres_table.get_genre_name(game['genre_id'])

    # Формирование карточки игры
    game_info = f"Название: {game['name']}\n" \
                f"Жанр: {genre_name}\n" \
                f"Описание: {game['description']}\n" \
                f"Цена: {game['price']}"

    # Создание медиагруппы из фотографий
    media = types.MediaGroup()
    # Добавляем первую фотографию с подписью
    media.attach_photo(game['photos'][0], caption=game_info)
    # Добавляем остальные фотографии без подписи
    for photo in game['photos'][1:]:
        media.attach_photo(photo)

    # Добавление кнопок "Удалить" и "Назад"
    delete_button = types.InlineKeyboardButton("Удалить", callback_data=f"delete_confirm:{game_id}")
    back_button = types.InlineKeyboardButton("Назад", callback_data="back")
    keyboard = types.InlineKeyboardMarkup().add(delete_button, back_button)

    # Удаление предыдущего сообщения
    await bot_admin.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
    # Отправка карточки игры с кнопками
    await bot_admin.send_media_group(chat_id=query.message.chat.id, media=media)
    await bot_admin.send_message(chat_id=query.message.chat.id, text="Подтвердите удаление товара:", reply_markup=keyboard)


@dp_admin.callback_query_handler(lambda c: c.data == 'back', state=DeleteGameState.ConfirmDelete)
async def back_button(query: types.CallbackQuery, state: FSMContext):
     # Удаление предыдущего сообщения
    await bot_admin.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id - 1)
    await delete_handler(query, state)


@dp_admin.callback_query_handler(lambda query: query.data.startswith("delete_confirm:"), state=DeleteGameState.ConfirmDelete)
async def delete_confirm_handler(query: types.CallbackQuery, state: FSMContext):
    await query.answer()

    game_id = query.data.split(":")[1]

    games_table = GamesTable()
    games_table.delete_game(game_id)

    await bot_admin.send_message(chat_id=query.message.chat.id, text="Игра успешно удалена.")
    await bot_admin.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id - 1)
    await delete_handler(query, state)


@dp_admin.callback_query_handler(lambda query: query.data == 'next', state=EditGameState.ConfirmEdit)
@dp_admin.callback_query_handler(lambda query: query.data == "next", state=DeleteGameState.ConfirmDelete)
async def handle_next_button(query: types.CallbackQuery, state: FSMContext):
    await query.answer()
    data = await state.get_data()
    offset = data['offset'] # получаем текущее смещение
    offset += 5 # увеличиваем смещение на 5

    games_table = GamesTable()
    games = games_table.select_rows(limit=5, offset=offset) # получаем следующие пять игр
    if not games:
        await query.answer('Дальше игр нет.', show_alert=True)
        return # если нет игр, выходим из обработчика


    await state.update_data(offset=offset) # обновляем смещение в state data

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for game in games:
        game_id = game[0]
        game_name = game[1]
        button = types.InlineKeyboardButton(game_name, callback_data=f"game_id:{game_id}")
        keyboard.add(button)

    # добавляем кнопку стрелки влево
    prev_button = types.InlineKeyboardButton("⬅️", callback_data="prev")
    # добавляем кнопку стрелки вправо
    next_button = types.InlineKeyboardButton("➡️", callback_data="next")
    # добавляем кнопку выхода
    cancel_button = types.InlineKeyboardButton("❌", callback_data="cancel")
    keyboard.row(prev_button, cancel_button, next_button)

    await bot_admin.edit_message_reply_markup(chat_id=query.message.chat.id, message_id=query.message.message_id,
                                              reply_markup=keyboard)


@dp_admin.callback_query_handler(lambda query: query.data == "prev", state=EditGameState.ConfirmEdit)
@dp_admin.callback_query_handler(lambda query: query.data == "prev", state=DeleteGameState.ConfirmDelete)
async def handle_prev_button(query: types.CallbackQuery, state: FSMContext):
    await query.answer()
    data = await state.get_data()
    offset = data['offset'] # получаем текущее смещение
    offset -= 5 # уменьшаем смещение на 5

    games_table = GamesTable()
    games = games_table.select_rows(limit=5, offset=offset) # получаем предыдущие пять игр
    if not games:
        await query.answer('Дальше игр нет.', show_alert=True)
        return # если нет игр, выходим из обработчика


    await state.update_data(offset=offset) # обновляем смещение в state data

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for game in games:
        game_id = game[0]
        game_name = game[1]
        button = types.InlineKeyboardButton(game_name, callback_data=f"game_id:{game_id}")
        keyboard.add(button)

    # добавляем кнопку стрелки влево
    prev_button = types.InlineKeyboardButton("⬅️", callback_data="prev")
    # добавляем кнопку стрелки вправо
    next_button = types.InlineKeyboardButton("➡️", callback_data="next")
    # добавляем кнопку выхода
    cancel_button = types.InlineKeyboardButton("❌", callback_data="cancel")
    
    if offset == 0:
        keyboard.row(cancel_button, next_button) # если смещение равно нулю, не показываем кнопку влево
    else:
        keyboard.row(prev_button, cancel_button, next_button)

    await bot_admin.edit_message_reply_markup(chat_id=query.message.chat.id, message_id=query.message.message_id,
                                              reply_markup=keyboard)


@dp_admin.callback_query_handler(lambda query: query.data == "cancel", state=DeleteGameState.ConfirmDelete)
async def handle_cancel_button(query: types.CallbackQuery, state: FSMContext):
    await query.answer()

    # Выход из режима удаления
    await state.reset_state()

    await bot_admin.send_message(chat_id=query.message.chat.id, text="Выход из режима удаления.")