import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from src import config, handlers
from src.utils.setup import dir_setup, logging_setup


async def start_bot() -> None:
    "Run bot"
    # creating instances bot and dispatcher
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
        ),
    )
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(
        handlers.main.router,
    )
    # starting bot polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


def run() -> None:
    "Start project"
    dir_setup()
    logging_setup()
    asyncio.run(start_bot())
