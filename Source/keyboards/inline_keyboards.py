from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from database.crud import Crud

async def on_start_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Получить PDF", callback_data="get_pdf")]
    ])
    return kb

async def on_admin_start_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Список уроков"), KeyboardButton(text="Список пользователей")],
        [KeyboardButton(text="Добавить урок"), KeyboardButton(text="Добавить/Изменить стартовый PDF")],
        [KeyboardButton(text="Добавить контент к уроку")]
    ])
    return kb

async def all_lessons_kb(crud: Crud, user_id: str) -> InlineKeyboardMarkup:
    lessons = crud.get_all_unarchived_lessons()
    completed_lessons = crud.get_completed_lessons(user_id)
    
    ikb = []
    for i in range(0, len(lessons)):
        if lessons[i].uid in completed_lessons:
            ikb.append([InlineKeyboardButton(text=f"✅ Урок {i+1}", callback_data=f"lesson_{lessons[i].uid}")])
        else:
            ikb.append([InlineKeyboardButton(text=f"Урок {i+1}", callback_data=f"lesson_{lessons[i].uid}")])

    kb = InlineKeyboardMarkup(inline_keyboard=ikb)
    return kb

async def link_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="ПЕРЕЙТИ К ОПИСАНИЮ КУРСА", url="http://aganare.ru/astral")]
    ])
    return kb
