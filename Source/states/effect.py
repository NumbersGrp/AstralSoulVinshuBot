from aiogram.fsm.state import StatesGroup, State

class Effect(StatesGroup):
    message_id = State()

class StartPdf(StatesGroup):
    waiting_for_document = State()