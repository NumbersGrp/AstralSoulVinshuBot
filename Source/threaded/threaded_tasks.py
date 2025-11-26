from database.crud import Crud
import asyncio
import threading
from threading import Thread

async def check_user_complete_periodically(bot):
    """Асинхронная периодическая проверка в основном цикле событий"""
    while True:
        try:
            print("Выполняю проверку пользователей...")
            crud = Crud()
            users = crud.get_all_users()
            for user in users:
                if len(crud.get_completed_lessons(user.uid)) >= len(crud.get_all_unarchived_lessons()):
                    print(f"Пользователь {user.uid} завершил все уроки!")
                    if not user.end_message_sended:
                        await bot.send_message(
                            chat_id=user.chat_id, 
                            text="Поздравляем! Вы завершили все уроки!"
                        )
                        crud.set_all_lessons_complete(user.uid)
                else:
                    lessons = crud.get_all_unarchived_lessons()
                    completed = crud.get_completed_lessons(user.uid)
                    for i in lessons:
                        if i.uid not in completed:
                            print(f"Отправлю ежедневный урок {i.title} пользователю {user.uid}")
                            try:
                                await bot.forward_message(chat_id=user.chat_id, from_chat_id=i.chat_id, message_id=i.content_message_id)
                                crud.complete_lesson(i.uid, user.uid)
                            except:
                                pass
                            break
                    
        except Exception as ex:
            print( ex )
            
        await asyncio.sleep(24 * 60 * 60)  # Ждем 1 минуту
