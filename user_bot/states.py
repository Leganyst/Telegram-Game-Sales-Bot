from aiogram.dispatcher.filters.state import State, StatesGroup

class BuyGameState(StatesGroup):
    SelectGenre = State()
    SelectGame = State()
    ChooseGame = State()
    WaitPaying = State()