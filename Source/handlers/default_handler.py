from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from core.bot import dp, bot
from database.crud import Crud
from keyboards.inline_keyboards import *
from aiogram import F
from states.effect import Effect
from states.effect import StartPdf
from states.lesson_manager import AddNewLesson
from states.lesson_manager import AddLessonContent
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
import asyncio


crud = Crud()

WELCOME_TEXT = ''
with open("Source/content/welcome_text.txt", "r") as f:
    WELCOME_TEXT = f.read()


@dp.message(Command("start"))
async def start_handler(message: Message, state: FSMContext = None):
    user = crud.get_user(message.from_user.id)
    if user is None:
        crud.create_user(message.from_user.username, message.from_user.id, chat_id=message.chat.id)
    user = crud.get_user(message.from_user.id)
    if user.role == "admin":
        sent_message = await message.answer("Добро пожаловать, в админ панель!", reply_markup=await on_admin_start_kb())
    else:
        sent_message = await message.answer(WELCOME_TEXT, reply_markup=await on_start_kb())
    await state.set_state(Effect.message_id)
    await state.update_data(message_id=sent_message.message_id)
    await state.update_data(user_id=user.uid)
    await state.update_data(chat_id=message.chat.id)

@dp.message(F.text.lower() == "добавить урок")
async def add_lesson_entry(message: Message, state: FSMContext = None):
    user = crud.get_user(message.from_user.id)
    if user is None or user.role != "admin":
        await message.answer("У вас нет прав на выполнение этой команды.")
        return
    await state.set_state(AddNewLesson.title)
    await message.answer("Введите заголовок урока:")

@dp.message(StateFilter(AddNewLesson.title))
async def add_lesson_set_title(message: Message, state: FSMContext = None):
    user = crud.get_user(message.from_user.id)
    if user is None or user.role != "admin":
        await message.answer("У вас нет прав на выполнение этой команды.")
        return
    title = (message.text or "").strip()
    if not title:
        await message.answer("Заголовок не может быть пустым. Введите заголовок урока:")
        return
    await state.update_data(title=title)
    await state.set_state(AddNewLesson.content_message_id)
    await message.answer("Отправьте или перешлите сообщение с контентом урока. Его ID будет сохранён.")

@dp.message(StateFilter(AddNewLesson.content_message_id))
async def add_lesson_set_message_id(message: Message, state: FSMContext = None):
    user = crud.get_user(message.from_user.id)
    if user is None or user.role != "admin":
        await message.answer("У вас нет прав на выполнение этой команды.")
        return

    text_lower = (message.text or "").strip().lower()
    data = await state.get_data()
    title = data.get("title", "")
    lesson_uid = data.get("lesson_uid")

    # If admin sent 'Готово' finish collecting
    if text_lower == "готово":
        await state.clear()
        if lesson_uid:
            await message.answer("Урок и контент сохранены.")
        else:
            await message.answer("Невозможно сохранить урок: не было отправлено ни одного сообщения.")
        return

    # If lesson not yet created, create it using the first message as main content
    if not lesson_uid:
        try:
            lesson = crud.create_lesson(title=title, content_message_id=message.message_id, archived=False, chat_id=message.chat.id)
            await state.update_data(lesson_uid=lesson.uid)
            await message.answer(f"Урок создан. Название: {lesson.title}\nТеперь отправляйте остальные сообщения для добавления в урок. Когда закончите, отправьте слово 'Готово'.")
            return
        except Exception as e:
            await message.answer(f"Ошибка при создании урока: {e}")
            await state.clear()
            return

    # For subsequent messages, add them as lesson content (store message_id for forwarding)
    try:
        crud.add_lesson_content(lesson_uid=lesson_uid, message_id=message.message_id)
        await message.answer("Контент добавлен.")
    except Exception as e:
        await message.answer(f"Ошибка при добавлении контента: {e}")

@dp.callback_query(F.data == "get_pdf")
async def get_pdf_handler(message: Message, state: FSMContext = None):
    data = await state.get_data()
    message_id = data.get("message_id")
    chat_id = data.get("chat_id")
    user_id = data.get("user_id")
    
    try:
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="PDF-файл будет отправлен вам в чат.")
        await asyncio.sleep(2)
        for i in range(5):
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"Начинаем наш путь через ... {5-i}")
            await asyncio.sleep(1)
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="")
    except:
        pass

    file_id = crud.get_setting("start_pdf_id")
    if file_id:
        try:
            await bot.send_message(chat_id=chat_id, text="🙏🏻🙏🏻🙏🏻")
            await bot.send_document(chat_id=chat_id, document=file_id)
        except Exception:
            await bot.send_message(chat_id=chat_id, text="Не удалось отправить PDF. Проверьте корректность файла.")
    else:
        await bot.send_message(chat_id=chat_id, text="Стартовый PDF не настроен. Обратитесь к администратору.")
    await bot.send_message(chat_id=chat_id, text="Ваши уроки:", reply_markup=await all_lessons_kb(crud, user_id))

@dp.message(F.text.lower() == "список пользователей")
async def list_users_handler(message: Message, state: FSMContext = None):
    user = crud.get_user(message.from_user.id)
    if user is None or user.role != "admin":
        await message.answer("У вас нет прав на выполнение этой команды.")
        return

    text = "Список пользователей:\n"
    
    for user in crud.get_all_users():
        text += f"@{user.tusername}\n"
        text += f"ID: {user.tid}\n"
        text += f"Роль: {user.role}\n"
        text += f"Дата регистрации: {user.created_at}\n"
        text += f"Дата последнего обновления: {user.updated_at}\n"
        text += "\n"
    
    await message.answer(text)


@dp.message(F.text.lower() == "список уроков")
async def list_lessons_handler(message: Message, state: FSMContext = None):
    user = crud.get_user(message.from_user.id)
    if user is None or user.role != "admin":
        await message.answer("У вас нет прав на выполнение этой команды.")
        return

    text = "Список уроков:\n"
    
    for lesson in crud.get_all_lessons():
        text += f"ID: {lesson.uid}\n"
        text += f"Название: {lesson.title}\n"
        text += f"ID сообщения с контентом: {lesson.content_message_id}\n"
        try:
            extra = len(crud.get_lesson_contents(lesson.uid))
            text += f"Доп. контента: {extra}\n"
        except Exception:
            pass
        text += f"Архив: {lesson.archived}\n"
        text += f"Дата создания: {lesson.created_at}\n"
        text += f"Дата последнего обновления: {lesson.updated_at}\n"
        text += "\n"
    
    await message.answer(text)

@dp.message(F.text.lower() == "добавить/изменить стартовый pdf")
async def start_pdf_entry(message: Message, state: FSMContext = None):
    user = crud.get_user(message.from_user.id)
    if user is None or user.role != "admin":
        await message.answer("У вас нет прав на выполнение этой команды.")
        return
    await state.set_state(StartPdf.waiting_for_document)
    await message.answer("Отправьте PDF-документ, который будет стартовым для пользователей.")

@dp.message(StateFilter(StartPdf.waiting_for_document))
async def start_pdf_save(message: Message, state: FSMContext = None):
    user = crud.get_user(message.from_user.id)
    if user is None or user.role != "admin":
        await message.answer("У вас нет прав на выполнение этой команды.")
        return
    if not message.document or (message.document and message.document.mime_type != "application/pdf"):
        await message.answer("Пожалуйста, отправьте PDF-документ.")
        return
    file_id = message.document.file_id
    crud.set_setting("start_pdf_id", file_id)
    await state.clear()
    await message.answer("Стартовый PDF сохранён и будет отправляться по кнопке 'Получить PDF'.")


@dp.callback_query(F.data.startswith("lesson_"))
async def lesson_handler(callback_query: CallbackQuery, state: FSMContext = None):
    user = crud.get_user(callback_query.from_user.id)
    if user is None:
        await callback_query.answer("У вас нет прав на выполнение этой команды.")
        return
    lesson_id = callback_query.data.split("_")[1]
    lesson = crud.get_lesson(lesson_id)
    if lesson is None:
        await callback_query.answer("Урок не найден.")
        return
    await bot.send_message(chat_id=callback_query.from_user.id, text=lesson.title)
    if lesson.chat_id:
        try:
            await bot.forward_message(chat_id=callback_query.from_user.id, from_chat_id=lesson.chat_id, message_id=lesson.content_message_id)
            if lesson.uid == "c29cc385-baa7-4bf8-945f-ba5730335dad":
                await bot.send_message(chat_id=callback_query.from_user.id, text="Ссылка: http://aganare.ru/astral", reply_markup=await link_kb())
                return
        except Exception:
            await bot.send_message(chat_id=callback_query.from_user.id, text="Не удалось переслать контент урока.")
        try:
            contents = crud.get_lesson_contents(lesson.uid)
            for c in contents:
                # If content stored as a forwarded message previously, keep behavior
                if c.content_type == 'message' and c.message_id:
                    await bot.forward_message(chat_id=callback_query.from_user.id, from_chat_id=lesson.chat_id, message_id=c.message_id)
                elif c.content_type in ('photo','document','audio','video') and c.file_id:
                    # send by file_id
                    try:
                        if c.content_type == 'photo':
                            await bot.send_photo(chat_id=callback_query.from_user.id, photo=c.file_id)
                        elif c.content_type == 'document':
                            await bot.send_document(chat_id=callback_query.from_user.id, document=c.file_id)
                        elif c.content_type == 'audio':
                            await bot.send_audio(chat_id=callback_query.from_user.id, audio=c.file_id)
                        elif c.content_type == 'video':
                            await bot.send_video(chat_id=callback_query.from_user.id, video=c.file_id)
                    except Exception:
                        # fallback to forward
                        try:
                            if c.message_id:
                                await bot.forward_message(chat_id=callback_query.from_user.id, from_chat_id=lesson.chat_id, message_id=c.message_id)
                        except Exception:
                            pass
                elif c.content_type == 'text' and c.text:
                    await bot.send_message(chat_id=callback_query.from_user.id, text=c.text)
                elif c.content_type == 'url' and c.url:
                    await bot.send_message(chat_id=callback_query.from_user.id, text=c.url)
        except Exception:
            pass
    else:
        await bot.send_message(chat_id=callback_query.from_user.id, text="Чат хранения уроков не настроен. Обратитесь к администратору.")
    crud.complete_lesson(lesson_id, user.uid)
    await bot.send_message(chat_id=callback_query.from_user.id, text="Ваши уроки", reply_markup=await all_lessons_kb(crud, user.uid))
    
@dp.message(F.text.lower() == "установить чат хранения уроков")
async def set_lessons_storage_chat(message: Message, state: FSMContext = None):
    user = crud.get_user(message.from_user.id)
    if user is None or user.role != "admin":
        await message.answer("У вас нет прав на выполнение этой команды.")
        return
    crud.set_setting("lessons_storage_chat_id", str(message.chat.id))
    await message.answer("Чат хранения уроков установлен. Все уроки будут пересылаться по их message_id из этого чата.")

@dp.message(F.text.lower() == "добавить контент к уроку")
async def add_content_entry(message: Message, state: FSMContext = None):
    user = crud.get_user(message.from_user.id)
    if user is None or user.role != "admin":
        await message.answer("У вас нет прав на выполнение этой команды.")
        return
    await state.set_state(AddLessonContent.lesson_uid)
    await message.answer("Введите ID урока (uid), к которому добавить контент:")

@dp.message(StateFilter(AddLessonContent.lesson_uid))
async def add_content_set_lesson(message: Message, state: FSMContext = None):
    user = crud.get_user(message.from_user.id)
    if user is None or user.role != "admin":
        await message.answer("У вас нет прав на выполнение этой команды.")
        return
    lesson_uid = (message.text or "").strip()
    lesson = crud.get_lesson(lesson_uid)
    if lesson is None:
        await message.answer("Урок не найден. Введите корректный ID урока:")
        return
    await state.update_data(lesson_uid=lesson_uid)
    await state.set_state(AddLessonContent.collecting)
    await message.answer("Отправляйте сообщения для добавления в урок. Когда закончите, отправьте слово 'Готово'.")

@dp.message(StateFilter(AddLessonContent.collecting))
async def add_content_collect(message: Message, state: FSMContext = None):
    user = crud.get_user(message.from_user.id)
    if user is None or user.role != "admin":
        await message.answer("У вас нет прав на выполнение этой команды.")
        return
    text_lower = (message.text or "").strip().lower()
    if text_lower == "готово":
        await state.clear()
        await message.answer("Дополнительный контент добавлен.")
        return
    data = await state.get_data()
    lesson_uid = data.get("lesson_uid", "")
    lesson = crud.get_lesson(lesson_uid)
    if lesson is None:
        await message.answer("Урок не найден.")
        return
    # Determine content type and save accordingly
    try:
        if message.text and not message.entities:
            # plain text
            crud.create_content_item(lesson_uid=lesson_uid, content_type='text', text=message.text)
            await message.answer("Текстовый контент добавлен.")
            return
        # documents (including pdfs)
        if message.document:
            mime = message.document.mime_type or ''
            if mime == 'application/pdf':
                crud.create_content_item(lesson_uid=lesson_uid, content_type='document', file_id=message.document.file_id)
                await message.answer("PDF / документ добавлен.")
                return
            else:
                crud.create_content_item(lesson_uid=lesson_uid, content_type='document', file_id=message.document.file_id)
                await message.answer("Документ добавлен.")
                return
        if message.photo:
            # take the largest photo
            photo = message.photo[-1]
            crud.create_content_item(lesson_uid=lesson_uid, content_type='photo', file_id=photo.file_id)
            await message.answer("Изображение добавлено.")
            return
        if message.audio:
            crud.create_content_item(lesson_uid=lesson_uid, content_type='audio', file_id=message.audio.file_id)
            await message.answer("Аудио добавлено.")
            return
        if message.video:
            crud.create_content_item(lesson_uid=lesson_uid, content_type='video', file_id=message.video.file_id)
            await message.answer("Видео добавлено.")
            return
        # fallback: if the message was forwarded or contains other media, store by message_id for forwarding
        if message.forward_from or message.forward_from_chat or message.message_id:
            crud.add_lesson_content(lesson_uid=lesson_uid, message_id=message.message_id)
            await message.answer("Контент добавлен как пересланное сообщение.")
            return
        await message.answer("Не удалось распознать тип контента. Отправьте текст, фото, документ, аудио или видео.")
    except Exception as e:
        await message.answer(f"Ошибка при добавлении контента: {e}")
