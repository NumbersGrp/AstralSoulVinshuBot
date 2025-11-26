from aiogram import Bot, Dispatcher
from core.settings import settings
from aiogram.fsm.storage.memory import MemoryStorage

dp = Dispatcher(storage=MemoryStorage())
bot = Bot(token=settings.bot_token)