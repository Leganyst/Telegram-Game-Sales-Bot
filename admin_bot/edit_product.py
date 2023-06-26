from aiogram import types
from aiogram.dispatcher import FSMContext

from database.genres_table_operations import GenresTable
from database.games_table_operations import GamesTable
from .settings.config import dp_admin, bot_admin
from .states import EditGameState


async def send_game_card(game_id, chat_id):
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

    # Отправка карточки игры
    await bot_admin.send_media_group(chat_id, media)


def is_valid_price(price):
    try:
        price = float(price)
        if price > 0:
            return True
        else:
            return False
    except ValueError:
        return False


def update_game_column(game_id, column_name, new_value):
    games_table = GamesTable()
    games_table.update_game(game_id, {column_name: new_value})
    genres_table = GenresTable()
    updated_game = games_table.get_game_by_id(game_id)

    if updated_game:
        genre_name = genres_table.get_genre_name(updated_game['genre_id'])

        game_info = f"Название: {updated_game['name']}\n" \
                    f"Жанр: {genre_name}\n" \
                    f"Описание: {updated_game['description']}\n" \
                    f"Цена: {updated_game['price']}"

        media = types.MediaGroup()
        media.attach_photo(updated_game['photos'][0], caption=game_info)
        for photo in updated_game['photos'][1:]:
            media.attach_photo(photo)

        return media, f"{column_name.capitalize()} успешно обновлено!"

    else:
        return None, "Не удалось найти игру."

def make_keyboard():
        # Добавление кнопок для выбора редактирования и кнопки назад
    name_button = types.InlineKeyboardButton('Название', callback_data='edit_name')
    genre_button = types.InlineKeyboardButton('Жанр', callback_data='edit_genre')
    price_button = types.InlineKeyboardButton("Цену", callback_data='edit_price')
    photo_button = types.InlineKeyboardButton("Фото", callback_data='edit_photo')
    descriptipn_button = types.InlineKeyboardButton("Описание", callback_data='edit_description')
    back_button = types.InlineKeyboardButton("Назад", callback_data="back")
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(name_button, descriptipn_button, genre_button, photo_button, price_button)
    keyboard.add(back_button)
    return keyboard


# Старт каталога
@dp_admin.callback_query_handler(lambda query: query.data == 'edit') 
async def edit_handler(query: types.CallbackQuery, state: FSMContext): 
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

    await bot_admin.send_message(chat_id=query.message.chat.id, text="Выберите карточку игры для редактирования:", reply_markup=keyboard)
    
    # удаляем предыдущее сообщение
    await bot_admin.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)

    await state.set_state(EditGameState.ConfirmEdit)


@dp_admin.callback_query_handler(lambda query: query.data == 'cancel', state=EditGameState.ConfirmEdit)
async def handle_cancel_button_edit(query: types.CallbackQuery, state: FSMContext):
    await query.answer()

    # Выход из режима удаления
    await state.reset_state()

    await bot_admin.send_message(chat_id=query.message.chat.id, text="Выход из режима редактирования. /settings для настроек маркета.")


@dp_admin.callback_query_handler(lambda query: query.data.startswith("game_id:"), state=EditGameState.ConfirmEdit)
async def confirm_edit_handler(query: types.CallbackQuery, state: FSMContext):
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

    await state.update_data(game_id=game_id)
    # Удаление предыдущего сообщения
    await bot_admin.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
    # Отправка карточки игры с кнопками
    await bot_admin.send_media_group(chat_id=query.message.chat.id, media=media)
    await bot_admin.send_message(chat_id=query.message.chat.id, text="Выберите что собираетесь изменить:", reply_markup=make_keyboard())

    await EditGameState.Choose.set()


@dp_admin.callback_query_handler(lambda c: c.data == 'back', state=EditGameState.Choose)
async def back__edit_button(query: types.CallbackQuery, state: FSMContext):
     # Удаление предыдущего сообщения
    await bot_admin.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id - 1)
    await edit_handler(query, state)


@dp_admin.callback_query_handler(lambda query: query.data == 'edit_name', state=EditGameState.Choose)
async def edit_name_handler(query: types.CallbackQuery, state: FSMContext):
    await query.answer()

    # Отправляем запрос пользователю на ввод нового названия игры
    await bot_admin.send_message(chat_id=query.message.chat.id, text="Введите новое название игры:")

    # Переходим в состояние ожидания нового названия игры
    await EditGameState.Name.set()

@dp_admin.message_handler(state=EditGameState.Name)
async def save_new_name_handler(message: types.Message, state: FSMContext):
    new_name = message.text

    game_id = await state.get_data()
    if game_id:
        game_id = game_id['game_id']
        media, message_text = update_game_column(game_id, 'name', new_name)

        if media:
            await bot_admin.send_media_group(chat_id=message.chat.id, media=media)
        await bot_admin.send_message(chat_id=message.chat.id, text=message_text)
        await message.answer('Выберите дальнейшее действие:', reply_markup=make_keyboard())
    else:
        await bot_admin.send_message(chat_id=message.chat.id, text="Не удалось получить идентификатор игры.")
    await EditGameState.Choose.set()


@dp_admin.callback_query_handler(lambda query: query.data == 'edit_genre', state=EditGameState.Choose)
async def edit_genre_handler(query: types.CallbackQuery, state: FSMContext):
    await query.answer()

    genres_table = GenresTable()
    all_genres = genres_table.get_all_genres()

    if all_genres:
        genre_buttons = []
        for genre in all_genres:
            genre_id = genre[0]
            genre_name = genre[1]
            genre_button = types.InlineKeyboardButton(genre_name, callback_data=f'select_genre:{genre_id}')
            genre_buttons.append(genre_button)

        keyboard = types.InlineKeyboardMarkup(row_width=3)
        keyboard.add(*genre_buttons)

        await bot_admin.send_message(chat_id=query.message.chat.id, text="Выберите новый жанр игры:", reply_markup=keyboard)

    else:
        await bot_admin.send_message(chat_id=query.message.chat.id, text="Нет доступных жанров.")


@dp_admin.callback_query_handler(lambda query: query.data.startswith('select_genre:'), state=EditGameState.Choose)
async def select_genre_handler(query: types.CallbackQuery, state: FSMContext):
    await query.answer()

    genre_id = query.data.split(':')[1]

    game_id = await state.get_data()
    if game_id:
        game_id = game_id['game_id']
        genres_table = GenresTable()
        genre_name = genres_table.get_genre_name(genre_id)

        if genre_name:
            media, message_text = update_game_column(game_id, 'genre_id', genre_id)

            if media:
                await bot_admin.send_media_group(chat_id=query.message.chat.id, media=media)
            await bot_admin.send_message(chat_id=query.message.chat.id, text=message_text)
            await query.message.answer('Выберите дальнейшее действие:', reply_markup=make_keyboard())

        else:
            await bot_admin.send_message(chat_id=query.message.chat.id, text="Не удалось получить название жанра.")

    else:
        await bot_admin.send_message(chat_id=query.message.chat.id, text="Не удалось получить идентификатор игры.")

    await EditGameState.Choose.set()


@dp_admin.callback_query_handler(lambda query: query.data == 'edit_description', state=EditGameState.Choose)
async def edit_description_handler(query: types.CallbackQuery, state: FSMContext):
    await query.answer()

    await bot_admin.send_message(chat_id=query.message.chat.id, text="Введите новое описание игры:")
    await EditGameState.EditDescription.set()

@dp_admin.message_handler(state=EditGameState.EditDescription)
async def save_description_handler(message: types.Message, state: FSMContext):
    description = message.text.strip()

    game_id = await state.get_data()
    if game_id:
        game_id = game_id['game_id']

        if description:
            media, message_text = update_game_column(game_id, 'description', description)

            if media:
                await bot_admin.send_media_group(chat_id=message.chat.id, media=media)
            await bot_admin.send_message(chat_id=message.chat.id, text=message_text)
            await message.answer('Выберите дальнейшее действие:', reply_markup=make_keyboard())
        else:
            await bot_admin.send_message(chat_id=message.chat.id, text="Описание не может быть пустым.")

    else:
        await bot_admin.send_message(chat_id=message.chat.id, text="Не удалось получить идентификатор игры.")

    await EditGameState.Choose.set()

@dp_admin.callback_query_handler(lambda query: query.data == 'edit_price', state=EditGameState.Choose)
async def edit_price_handler(query: types.CallbackQuery, state: FSMContext):
    await query.answer()

    await bot_admin.send_message(chat_id=query.message.chat.id, text="Введите новую цену игры:")
    await EditGameState.EditPrice.set()

@dp_admin.message_handler(state=EditGameState.EditPrice)
async def save_price_handler(message: types.Message, state: FSMContext):
    price = message.text.strip()

    game_id = await state.get_data()
    if game_id:
        game_id = game_id['game_id']

        if price and is_valid_price(price):
            media, message_text = update_game_column(game_id, 'price', price)

            if media:
                await bot_admin.send_media_group(chat_id=message.chat.id, media=media)
            await bot_admin.send_message(chat_id=message.chat.id, text=message_text)
            await message.answer('Выберите дальнейшее действие:', reply_markup=make_keyboard())
        else:
            await bot_admin.send_message(chat_id=message.chat.id, text="Неверный формат цены.")

    else:
        await bot_admin.send_message(chat_id=message.chat.id, text="Не удалось получить идентификатор игры.")

    await EditGameState.Choose.set()


@dp_admin.callback_query_handler(lambda query: query.data == 'edit_photo', state=EditGameState.Choose)
async def edit_price_handler(query: types.CallbackQuery, state: FSMContext):
    await query.answer()

    await bot_admin.send_message(chat_id=query.message.chat.id, text="Отправьте до 10 фотографий:")
    await EditGameState.EditPhoto.set()


@dp_admin.message_handler(content_types=types.ContentTypes.PHOTO, state=EditGameState.EditPhoto)
async def edit_photo_save_handler(message: types.Message, state: FSMContext):
    # Получаем текущие данные из состояния
    game_data = await state.get_data()
    game_id = game_data['game_id']

    # Получаем список фотографий из состояния или создаем новый
    photos = game_data.get('photos', [])

    # Добавляем новую фотографию в список
    photos.append(message.photo[-1].file_id)

    # Обновляем данные в состоянии
    await state.update_data(photos=photos)

    # Проверяем количество фотографий в списке
    if len(photos) < 10:
        # Если меньше 10, то просим отправить еще
        await message.reply(f"Вы отправили {len(photos)} фотографий. Отправьте еще или нажмите /done.")
    else:
        # Если равно 10, то сохраняем фотографии в базе данных
        games_table = GamesTable()
        games_table.update_game_photos(game_id, photos)

        # Отправляем сообщение об успешном изменении фотографий
        await message.answer("Фотографии успешно изменены.")

        # Отправляем карточку товара с новыми фотографиями
        await send_game_card(game_id, message.chat.id)

        # Переходим в состояние выбора следующего действия
        await EditGameState.Choose.set()
        await message.answer('Выберите дальнейшее действие:', reply_markup=make_keyboard())
        


@dp_admin.message_handler(commands=['done'], state=EditGameState.EditPhoto)
async def done_photos_handler(message: types.Message, state: FSMContext):
    # Получаем текущие данные из состояния
    game_data = await state.get_data()
    game_id = game_data['game_id']

    # Получаем список фотографий из состояния
    photos = game_data.get('photos', [])

    # Если есть хотя бы одна фотография, сохраняем их в базе данных
    if photos:
        games_table = GamesTable()
        games_table.update_game_photos(game_id, photos)

        # Отправляем сообщение об успешном изменении фотографий
        await message.answer("Фотографии успешно изменены.")

        # Отправляем карточку товара с новыми фотографиями
        await send_game_card(game_id, message.chat.id)

    # Переходим в состояние выбора следующего действия
    await EditGameState.Choose.set()
    await message.answer('Выберите дальнейшее действие:', reply_markup=make_keyboard())



