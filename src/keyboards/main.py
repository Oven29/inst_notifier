from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


profile = lambda profile_id: InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Подписаться/отписаться от уведомлмений", callback_data=f"notifier {profile_id}")],
        [InlineKeyboardButton(text="Получить 3 последних поста", callback_data=f"posts {profile_id}")],
        [InlineKeyboardButton(text="Выгрузить истории пользователя", callback_data=f"stories {profile_id}")],
    ]
)
