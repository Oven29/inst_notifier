from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, InputMediaVideo
from aiogram.utils.media_group import MediaGroupBuilder

from src.inst.types import MediaType
from src.keyboards import main as kb
from src.utils.inst_parser import inst_parser


router = Router()


@router.message(Command('start'))
async def cmd_start(message: Message) -> None:
    await message.answer(
        text='Это бот для получения информации о пользователе Instagram\n'
            'Пришли username пользователя, информацию о котором хотите получить',
    )


@router.message()
async def get_profile(message: Message, state: FSMContext) -> None:
    try:
        username = message.text
        user_id = inst_parser.get_user_id(username)
        state_data = await state.get_data()
        is_sub = state_data.get(user_id)
        await message.answer(
            text=f'<a href="https://www.instagram.com/{username}">{username}</a>\nID пользователя: {user_id}\n' +
            (f'🟩 Вы подписаны на уведомления' if is_sub else '🟥 Вы не подписаны на уведомления'),
            reply_markup=kb.profile(user_id),
        )

    except:
        await message.answer(
            text='Пользователь не найден',
        )


@router.callback_query(F.data.startswith('notifier'))
async def notifier(call: CallbackQuery, state: FSMContext) -> None:
    await call.answer(
        text='Эта функция в разработке',
        show_alert=True,
    )


@router.callback_query(F.data.startswith('posts'))
async def get_posts(call: CallbackQuery) -> None:
    wait_mes = await call.message.answer('Идёт выгрузка постов...')
    _, user_id = call.data.split()
    posts = inst_parser.get_user_posts(user_id, count=3)

    for post in posts:
        builder = MediaGroupBuilder(
            caption=post.caption,
            media=[
                InputMediaPhoto(media=el.url) if el.type == MediaType.IMAGE.value else InputMediaVideo(media=el.url) 
                for el in post.media_list
            ],
        )
        await call.message.answer_media_group(media=builder.build())

    await wait_mes.delete()


@router.callback_query(F.data.startswith('stories'))
async def get_stories(call: CallbackQuery) -> None:
    wait_mes = await call.message.answer('Идёт выгрузка историй...')
    _, user_id = call.data.split()
    stories = inst_parser.get_user_stories(user_id)

    for i in range(0, len(stories), 10):
        builder = MediaGroupBuilder(
            caption=f'Истории пользователя {user_id}',
            media=[
                InputMediaPhoto(media=el.media.url) if el.media.type == MediaType.IMAGE.value else InputMediaVideo(media=el.media.url) 
                for el in stories[i:i+10]
            ],
        )
        await call.message.answer_media_group(media=builder.build())

    if len(stories) == 0:
        await wait_mes.edit_text('Пользователь не имеет историй')
    else:
        await wait_mes.delete()
