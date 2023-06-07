from aiogram import types
from aiogram.dispatcher.filters import Filter


class WhitelistFilter(Filter):
    def __init__(self, whitelist: list):
        self.whitelist = whitelist

    async def check(self, message: types.Message):
        user_id = message.from_user.id
        return user_id in self.whitelist