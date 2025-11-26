from aiogram.fsm.state import StatesGroup, State

class AddNewLesson(StatesGroup):
    title = State()
    content_message_id = State()
    archived = State()
    
class AddLessonContent(StatesGroup):
    lesson_uid = State()
    collecting = State()
    
