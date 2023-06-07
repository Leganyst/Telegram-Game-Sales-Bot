from aiogram.dispatcher import FSMContext
from aiogram import types

from .settings.config import dp_admin, bot_admin
from .states import AddCardState
from database.games_table_operations import GamesTable
from database.genres_table_operations import GenresTable

@dp_admin.callback_query_handler(lambda query: query.data == 'add')
async def add_handler(query: types.CallbackQuery, state: FSMContext):
    await query.answer()
    # Удаление предыдущего сообщения
    await bot_admin.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
    # Переход в состояние Start
    await state.set_state(AddCardState.FillName)
    # Отправка нового сообщения с инструкцией
    await bot_admin.send_message(chat_id=query.message.chat.id, text="Начнем создание игры. Заполните следующие поля:\nНазвание, описание, жанр, фото, цена")
    await bot_admin.send_message(chat_id=query.message.chat.id, text='Напишите название игры: ')

@dp_admin.message_handler(state=AddCardState.FillName)
async def fill_name_handler(message: types.Message, state: FSMContext):
    # Сохраняем имя игры в память
    await state.update_data(name=message.text)
    # Переходим к состоянию FillDescription
    await AddCardState.FillDescription.set()
    # Отправляем сообщение с просьбой ввести описание игры
    await message.answer("Введите описание игры:")

@dp_admin.message_handler(state=AddCardState.FillDescription)
async def fill_description_handler(message: types.Message, state: FSMContext):
    # Сохраняем описание игры в память
    await state.update_data(description=message.text)
    
    # Получаем все записи жанров из базы данных
    genre_table = GenresTable()
    genres = genre_table.get_all_genres()


    # Создаем инлайн клавиатуру с жанрами
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    for genre in genres:
        genre_id = genre[0]
        genre_name = genre[1]
        button = types.InlineKeyboardButton(genre_name, callback_data=f"genre_id:{genre_id}")
        keyboard.add(button)

    # Отправляем сообщение с просьбой выбрать жанр игры
    await message.answer("Выберите жанр игры:", reply_markup=keyboard)

    # Переходим к состоянию FillGenre
    await AddCardState.FillGenre.set()


@dp_admin.callback_query_handler(lambda query: query.data.startswith("genre_id:"), state=AddCardState.FillGenre)
async def fill_genre_handler(query: types.CallbackQuery, state: FSMContext):
    # Извлекаем genre_id из callback_data
    genre_id = query.data.split(":")[1]

    # Сохраняем genre_id в состоянии
    await state.update_data(genre=genre_id)
    await query.answer()

    # Переходим к состоянию FillPhoto
    await AddCardState.FillPhoto.set()

    # Отправляем сообщение с просьбой отправить фотографии игры
    await query.message.answer("Пришлите фотографии игры (до 10 штук):")


@dp_admin.message_handler(content_types=types.ContentTypes.PHOTO, state=AddCardState.FillPhoto)
async def fill_photos_handler(message: types.Message, state: FSMContext):
    # Получаем текущие данные из состояния
    game_data = await state.get_data()

    # Получаем список фотографий из состояния или создаем новый
    photos = game_data.get('photos', [])

    # Добавляем фотографию в список
    photos.append(message.photo[-1].file_id)

    # Обновляем данные в состоянии
    await state.update_data(photos=photos)

    # Проверяем количество фотографий в списке
    if len(photos) < 10:
        # Если меньше 10, то просим отправить еще
        await message.reply(f"Вы отправили {len(photos)} фотографий. Отправьте еще или нажмите /done.")
    else:
        # Если равно 10, то переходим к следующему состоянию
        await AddCardState.next()

        # Отправляем сообщение с просьбой ввести цену игры
        await message.reply("Введите цену игры:")


@dp_admin.message_handler(commands=['done'], state=AddCardState.FillPhoto)
async def done_photos_handler(message: types.Message, state: FSMContext):
    # Переходим к следующему состоянию
    await AddCardState.next()

    # Отправляем сообщение с просьбой ввести цену игры
    await message.reply("Введите цену игры:")


@dp_admin.message_handler(content_types=types.ContentTypes.TEXT, state=AddCardState.FillPrice)
async def fill_price_handler(message: types.Message, state: FSMContext):
    # Получаем текущие данные из состояния
    game_data = await state.get_data()

    # Получаем цену игры от пользователя
    price = message.text

    # Обновляем данные в состоянии
    game_data['price'] = price
    await state.update_data(game_data)

    # Получаем список фотографий из состояния
    photos = game_data.get('photos', [])

    # Получаем название жанра по genre_id
    genre_id = game_data['genre']
    genre_table = GenresTable()
    genre_name = genre_table.get_genre_name(genre_id)


    # Формируем текст карточки игры
    game_info = f"Название: {game_data['name']}\n" \
                f"Жанр: {genre_name}\n" \
                f"Описание: {game_data['description']}\n" \
                f"Цена: {game_data['price']}"

    # Создаем медиагруппу из фотографий
    media = types.MediaGroup()

    # Добавляем первую фотографию с подписью
    media.attach_photo(photos[0], caption=game_info)

    # Добавляем остальные фотографии без подписи
    for photo in photos[1:]:
        media.attach_photo(photo)

    # Отправляем медиагруппу
    await message.reply_media_group(media=media)

    # Предлагаем пользователю сохранить или удалить игру
    markup = types.InlineKeyboardMarkup(row_width=2)
    save_button = types.InlineKeyboardButton("Сохранить", callback_data="save")
    delete_button = types.InlineKeyboardButton("Удалить", callback_data="delete")
    markup.add(save_button, delete_button)

    await message.reply("Выберите действие:", reply_markup=markup)

    # Переходим в новое состояние
    await AddCardState.Confirm.set()


@dp_admin.callback_query_handler(lambda query: query.data == "save", state=AddCardState.Confirm)
async def save_game_handler(query: types.CallbackQuery, state: FSMContext):
    # Получаем текущие данные из состояния
    game_data = await state.get_data()

    # Извлекаем необходимые данные
    name = game_data['name']
    price = game_data['price']
    description = game_data['description']
    genre = game_data['genre']
    photos = game_data.get('photos', [])

    # Сохраняем данные в базу данных
    game_table = GamesTable()
    game_table.add_game(name, price, description, genre, photos)


    # Отправляем сообщение о сохранении
    await query.message.answer("Игра сохранена.")

    # Предлагаем пользователю выбрать дальнейшее действие
    markup = types.InlineKeyboardMarkup(row_width=2)
    continue_button = types.InlineKeyboardButton("Продолжить", callback_data="create")
    exit_button = types.InlineKeyboardButton("Выйти", callback_data="exit")
    markup.add(continue_button, exit_button)
    await query.answer()
    await query.message.answer("Выберите дальнейшее действие:", reply_markup=markup)

    # Переходим в новое состояние
    await AddCardState.Finalize.set()


@dp_admin.callback_query_handler(lambda query: query.data == "delete", state=AddCardState.Confirm)
async def delete_game_handler(query: types.CallbackQuery, state: FSMContext):
    # Очищаем данные в состоянии
    await state.reset_state()

    # Предлагаем пользователю создать новую карточку или выйти
    markup = types.InlineKeyboardMarkup(row_width=2)
    create_button = types.InlineKeyboardButton("Создать новую карточку", callback_data="create")
    exit_button = types.InlineKeyboardButton("Выйти", callback_data="exit")
    markup.add(create_button, exit_button)
    await query.answer()
    await query.message.answer("Данная карточка удалена. Что вы хотите сделать?", reply_markup=markup)

    # Переходим в новое состояние
    await AddCardState.Finalize.set()


@dp_admin.callback_query_handler(lambda c: c.data == 'exit', state=AddCardState.Finalize)
async def exit_for_add_card(query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await query.answer()
    await query.message.answer("Вы вышли из режима создания карточки продукта. /settings для настроек маркета.")

@dp_admin.callback_query_handler(lambda c: c.data == 'create', state=AddCardState.Finalize)
async def continue_new_card_make(query: types.CallbackQuery, state: FSMContext):
    await query.answer()
    await state.finish()
    await add_handler(query, state)