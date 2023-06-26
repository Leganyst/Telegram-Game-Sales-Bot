from admin_bot.settings.config import dp_admin, bot_admin
from admin_bot import *
from database import *
from user_bot import *

from aiogram import executor

import asyncio


async def main():
    await asyncio.gather(
        dp_admin.start_polling(),
    )

if __name__ == '__main__':
    asyncio.run(main())