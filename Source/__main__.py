from core.settings import settings
from database.database import create_session
import asyncio
from core.bot import dp, bot
from handlers.default_handler import *
from threaded.threaded_tasks import check_user_complete_periodically

async def main():
    print("Bot is running")
    
    # Запускаем фоновую задачу проверки пользователей
    asyncio.create_task(check_user_complete_periodically(bot))
    
    # Запускаем бота (это блокирующая операция)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())