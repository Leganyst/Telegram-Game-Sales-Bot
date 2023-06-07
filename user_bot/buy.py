from aiogram.dispatcher import FSMContext
from aiogram import types
from aiogram.types import PreCheckoutQuery

from admin_bot.settings.config import dp_admin, bot_admin, PROVIDER_TOKEN
from database.games_table_operations import GamesTable
from database.genres_table_operations import GenresTable
from .states import BuyGameState

@dp_admin.message_handler(commands=['buy'])
async def buy_handler(message: types.Message):
    # Получаем список жанров из таблицы genres
    genres_table = GenresTable()
    genres = genres_table.get_all_genres()

    # Разделяем жанры на столбцы для формирования клавиатуры
    columns = 3
    keyboard = types.InlineKeyboardMarkup(row_width=columns)
    for genre in genres:
        genre_id = genre[0]
        genre_name = genre[1]
        button = types.InlineKeyboardButton(genre_name, callback_data=f"genre_id:{genre_id}")
        keyboard.add(button)

    # Отправляем сообщение с просьбой выбрать жанр
    await bot_admin.send_message(chat_id=message.chat.id, text="Выберите жанр игры:", reply_markup=keyboard)

    # Устанавливаем первое состояние после команды /buy
    await BuyGameState.SelectGenre.set()


@dp_admin.callback_query_handler(lambda query: query.data.startswith('genre_id:'), state=BuyGameState.SelectGenre)
async def select_genre_handler(query: types.CallbackQuery, state: FSMContext):
    # Получаем genre_id из callback_data
    genre_id = query.data.split(':')[1]

    # Получаем список игр по выбранному жанру из таблицы games
    games_table = GamesTable()
    games = games_table.select_rows_by_genre(genre_id, limit=5, offset=0)

    offset = 0  # Устанавливаем смещение на 0
    await state.update_data(offset=offset)  # Сохраняем смещение в state data
    await state.update_data(genre_id=genre_id)

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for game in games:
        game_id = game[0]
        game_name = game[1]
        button = types.InlineKeyboardButton(game_name, callback_data=f"game_id:{game_id}")
        keyboard.add(button)

    # Добавляем кнопку стрелки вправо
    next_button = types.InlineKeyboardButton("➡️", callback_data="next")
    # Добавляем кнопку выхода
    cancel_button = types.InlineKeyboardButton("❌", callback_data="cancel")
    keyboard.row(cancel_button, next_button)

    await bot_admin.send_message(chat_id=query.message.chat.id, text="Выберите игру:", reply_markup=keyboard)

    # Удаляем предыдущее сообщение
    await bot_admin.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)

    # Устанавливаем состояние для выбора игры
    await BuyGameState.SelectGame.set()


@dp_admin.callback_query_handler(lambda query: query.data == 'next', state=BuyGameState.SelectGame)
async def handle_next_button(query: types.CallbackQuery, state: FSMContext):
    await query.answer()
    data = await state.get_data()
    offset = data['offset']
    genre_id = data['genre_id']

    offset += 5

    games_table = GamesTable()
    games = games_table.select_rows_by_genre(genre_id, limit=5, offset=offset)
    if not games:
        await query.answer('Дальше игр нет.', show_alert=True)
        return

    await state.update_data(offset=offset)

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for game in games:
        game_id = game[0]
        game_name = game[1]
        button = types.InlineKeyboardButton(game_name, callback_data=f"game_id:{game_id}")
        keyboard.add(button)

    prev_button = types.InlineKeyboardButton("⬅️", callback_data="prev")
    next_button = types.InlineKeyboardButton("➡️", callback_data="next")
    cancel_button = types.InlineKeyboardButton("❌", callback_data="cancel")
    keyboard.row(prev_button, cancel_button, next_button)

    await bot_admin.edit_message_reply_markup(chat_id=query.message.chat.id, message_id=query.message.message_id,
                                             reply_markup=keyboard)


@dp_admin.callback_query_handler(lambda query: query.data == "prev", state=BuyGameState.SelectGame)
async def handle_prev_button(query: types.CallbackQuery, state: FSMContext):
    await query.answer()
    data = await state.get_data()
    offset = data['offset']
    genre_id = data['genre_id']

    offset -= 5

    if offset < 0:
        offset = 0

    games_table = GamesTable()
    games = games_table.select_rows_by_genre(genre_id, limit=5, offset=offset)
    if not games:
        await query.answer('Дальше игр нет.', show_alert=True)
        return

    await state.update_data(offset=offset)

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for game in games:
        game_id = game[0]
        game_name = game[1]
        button = types.InlineKeyboardButton(game_name, callback_data=f"game_id:{game_id}")
        keyboard.add(button)

    prev_button = types.InlineKeyboardButton("⬅️", callback_data="prev")
    next_button = types.InlineKeyboardButton("➡️", callback_data="next")
    cancel_button = types.InlineKeyboardButton("❌", callback_data="cancel")

    if offset == 0:
        keyboard.row(cancel_button, next_button)
    else:
        keyboard.row(prev_button, cancel_button, next_button)

    await bot_admin.edit_message_reply_markup(chat_id=query.message.chat.id, message_id=query.message.message_id,
                                             reply_markup=keyboard)


@dp_admin.callback_query_handler(lambda query: query.data == "cancel", state=BuyGameState.SelectGame)
async def handle_cancel_button(query: types.CallbackQuery, state: FSMContext):
    await query.answer()

    await state.finish()

    await bot_admin.send_message(chat_id=query.message.chat.id, text="Выход из режима покупки. /buy для просмотра игр")



@dp_admin.callback_query_handler(lambda query: query.data.startswith("game_id:"), state=BuyGameState.SelectGame)
async def confirm_buy_handler(query: types.CallbackQuery, state: FSMContext):
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
    
    pay_button = types.InlineKeyboardButton(f"Оплатить {game['price']}", callback_data=f"pay:{int(game['price'])}")
    keyboard = types.InlineKeyboardMarkup().add(pay_button)

    await state.update_data(game_name=game['name'])
    await state.update_data(game_description=game['description'])

    await bot_admin.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
    await bot_admin.send_media_group(chat_id=query.message.chat.id, media=media)
    await bot_admin.send_message(chat_id=query.message.chat.id, text='Необходима оплата', reply_markup=keyboard)
    await BuyGameState.WaitPaying.set()

@dp_admin.callback_query_handler(state=BuyGameState.WaitPaying)
async def start_payment_handler(query: types.CallbackQuery, state: FSMContext):
    # Получаем цену товара из callback_data
    price = int(query.data.split(':')[1]) * 100

    game_info = await state.get_data

    if price < 10 * 100:
        # Цена товара меньше 10 рублей, выводим сообщение об ошибке
        await query.message.answer('Цена товара слишком низкая. Оплата недоступна.')
        return

    await bot_admin.send_invoice(
        chat_id=query.message.chat.id,
        title=game_info['game_name'],
        description=game_info['game_description'],
        payload='custom_payload',
        provider_token=PROVIDER_TOKEN,
        currency='RUB',
        prices=[
            types.LabeledPrice(label='Цена товара', amount=price)
        ],
        start_parameter='payment',
        need_shipping_address=True
    )

# Обработчик предварительного запроса на оплату
@dp_admin.pre_checkout_query_handler(state=BuyGameState.WaitPaying)
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery, state: FSMContext):
    await bot_admin.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

# Обработчик успешной оплаты
@dp_admin.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT, state=BuyGameState.WaitPaying)
async def successful_payment_handler(message: types.Message, state: FSMContext):
    await bot_admin.send_message(chat_id=message.chat.id, text='Оплата прошла успешно!')
    await state.reset_state()  # Сброс состояния

# Обработчик получения адреса доставки
@dp_admin.shipping_query_handler(state=BuyGameState.WaitPaying)
async def process_shipping_query(shipping_query: types.ShippingQuery, state: FSMContext):
    # Получаем информацию о заказе и адресе доставки
    order_info = shipping_query.order_info
    shipping_address = order_info.shipping_address
    # Далее можно обработать полученные данные и сохранить их, если необходимо
    # ...

# Обработчик успешного изменения адреса доставки
@dp_admin.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT, state=BuyGameState.WaitPaying)
async def successful_shipping_handler(message: types.Message, state: FSMContext):
    await bot_admin.send_message(chat_id=message.chat.id, text='Адрес доставки изменен!')
    await state.reset_state()  # Сброс состояния