from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery


router = Router()


@router.message(Command('start'))
async def cmd_start(message: Message) -> None:
    await message.answer('Hello, world!')
