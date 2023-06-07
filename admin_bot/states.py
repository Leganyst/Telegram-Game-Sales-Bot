from aiogram.dispatcher.filters.state import State, StatesGroup

class AddCardState(StatesGroup):
    Start = State()
    FillName = State()
    FillDescription = State()
    FillGenre = State()
    FillPhoto = State()
    FillPrice = State()
    Confirm = State()
    Finalize = State()

class DeleteGameState(StatesGroup):
    ConfirmDelete = State()

class AddGenreState(StatesGroup):
    waiting_for_genre_name = State()

class EditGameState(StatesGroup):
    ConfirmEdit = State()
    Choose = State()
    Name = State()
    EditDescription = State()
    EditPrice = State()
    EditPhoto = State()