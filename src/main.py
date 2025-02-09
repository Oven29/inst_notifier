import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from src import config, handlers
from src.utils.scheduler import scheduler
from src.utils.setup import dir_setup, logging_setup


async def on_startup() -> None:
    "On startup"
    scheduler.start()


async def on_shutdown() -> None:
    "On shutdown"
    scheduler.shutdown()


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
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    # starting bot polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


def run() -> None:
    "Start project"
    dir_setup()
    logging_setup()
    asyncio.run(start_bot())
