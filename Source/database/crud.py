from database.models import Lesson, User, Setting, UserLessonProgress, LessonContent
from database.database import create_session

session = create_session()

def ensure_session_ready():
    try:
        session.rollback()
    except Exception:
        pass

class UserManager:
    def __init__(self):
        self.create_default_admins()

    def create_default_admins(self):
        try:
            #self.create_user("twelvefacedjanu", 7978367962, role="admin")
            self.create_user("AlinaVinshu", 724595286, role="admin")
        except Exception as e:
            session.rollback()
            raise e

    def set_all_lessons_complete(self, user_uid: str):
        try:
            ensure_session_ready()
            user = session.query(User).filter(User.uid == user_uid).first()
            user.end_message_sended = True
            session.commit()
        except Exception as e:
            session.rollback()
            raise e

    def create_user(self, tusername: str, tid: int, role: str = "user", chat_id: int = 0):
        try:
            ensure_session_ready()
            if self.get_user(tid): return self.get_user(tid)
            user = User(tusername=tusername, tid=tid, role=role, chat_id=chat_id)
            session.add(user)
            session.commit()
            return user
        except Exception as e:
            session.rollback()
            raise e
        
    def get_user(self, tid: int):
        try:
            ensure_session_ready()
            user = session.query(User).filter(User.tid == tid).first()
            return user
        except Exception as e:
            session.rollback()
            raise e

    def get_all_users(self):
        try:
            ensure_session_ready()
            users = session.query(User).all()
            return users
        except Exception as e:
            session.rollback()
            raise e


class LessonManager:
    def __init__(self):
        pass

    def get_all_lessons(self):
        try:
            ensure_session_ready()
            lessons = session.query(Lesson).all()
            return lessons
        except Exception as e:
            session.rollback()
            raise e

    def get_lesson(self, uid: str):
        try:
            ensure_session_ready()
            lesson = session.query(Lesson).filter(Lesson.uid == uid).first()
            return lesson
        except Exception as e:
            session.rollback()
            raise e

    def create_lesson(self, title: str = '', content_message_id: int = 0, archived: bool = False, chat_id: int = 0):
        try:
            ensure_session_ready()
            lesson = Lesson(title=title, content_message_id=content_message_id, archived=archived, chat_id=chat_id)
            session.add(lesson)
            session.commit()
            return lesson
        except Exception as e:
            session.rollback()
            raise e
        
    def get_all_unarchived_lessons(self):
        try:
            ensure_session_ready()
            lessons = session.query(Lesson).filter(Lesson.archived == False).all()
            return lessons
        except Exception as e:
            session.rollback()
            raise e

    def get_completed_lessons(self, user_id: str):
        try:
            ensure_session_ready()
            completed_lessons = session.query(UserLessonProgress).filter(UserLessonProgress.user_uid == user_id).all()
            return [progress.at_lesson_uid for progress in completed_lessons]
        except Exception as e:
            session.rollback()
            raise e

    def complete_lesson(self, lesson_id: str, user_id: str):
        try:
            ensure_session_ready()
            user_completed = self.get_completed_lessons(user_id)
            if lesson_id in user_completed:
                return False
            progress = UserLessonProgress(user_uid=user_id, at_lesson_uid=lesson_id)
            if progress:
                session.add(progress)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e

    def add_lesson_content(self, lesson_uid: str, message_id: int):
        """
        Backward-compatible helper: create a lesson content entry of type 'message' using an existing forwarded message id.
        """
        try:
            ensure_session_ready()
            count = session.query(LessonContent).filter(LessonContent.lesson_uid == lesson_uid).count()
            lc = LessonContent(lesson_uid=lesson_uid, message_id=message_id, position=count, content_type='message')
            session.add(lc)
            session.commit()
            return lc
        except Exception as e:
            session.rollback()
            raise e

    def get_lesson_contents(self, lesson_uid: str):
        try:
            ensure_session_ready()
            contents = session.query(LessonContent).filter(LessonContent.lesson_uid == lesson_uid).order_by(LessonContent.position.asc()).all()
            return contents
        except Exception as e:
            session.rollback()
            raise e

    # New CRUD for content items
    def create_content_item(self, lesson_uid: str, content_type: str = 'text', file_id: str = None, file_path: str = None, text: str = None, url: str = None, metadata: str = None, position: int = None):
        try:
            ensure_session_ready()
            if position is None:
                position = session.query(LessonContent).filter(LessonContent.lesson_uid == lesson_uid).count()
            ci = LessonContent(lesson_uid=lesson_uid, content_type=content_type, file_id=file_id, file_path=file_path, text=text, url=url, metadata_json=metadata, position=position)
            session.add(ci)
            session.commit()
            return ci
        except Exception as e:
            session.rollback()
            raise e

    def get_content_item(self, uid: str):
        try:
            ensure_session_ready()
            ci = session.query(LessonContent).filter(LessonContent.uid == uid).first()
            return ci
        except Exception as e:
            session.rollback()
            raise e

    def update_content_item(self, uid: str, **fields):
        try:
            ensure_session_ready()
            ci = session.query(LessonContent).filter(LessonContent.uid == uid).first()
            if not ci:
                return None
            for k, v in fields.items():
                if hasattr(ci, k):
                    setattr(ci, k, v)
            session.commit()
            return ci
        except Exception as e:
            session.rollback()
            raise e

    def delete_content_item(self, uid: str):
        try:
            ensure_session_ready()
            ci = session.query(LessonContent).filter(LessonContent.uid == uid).first()
            if not ci:
                return False
            session.delete(ci)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e

    def reorder_content_items(self, lesson_uid: str, ordered_uids: list):
        try:
            ensure_session_ready()
            for index, uid in enumerate(ordered_uids):
                session.query(LessonContent).filter(LessonContent.uid == uid, LessonContent.lesson_uid == lesson_uid).update({"position": index})
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e


class SettingsManager:
    def __init__(self):
        pass

    def get_setting(self, key: str):
        try:
            ensure_session_ready()
            s = session.query(Setting).filter(Setting.key == key).first()
            return s.value if s else None
        except Exception as e:
            session.rollback()
            raise e

    def set_setting(self, key: str, value: str):
        try:
            ensure_session_ready()
            s = session.query(Setting).filter(Setting.key == key).first()
            if s:
                s.value = value
            else:
                s = Setting(key=key, value=value)
                session.add(s)
            session.commit()
            return s
        except Exception as e:
            session.rollback()
            raise e


class Crud(UserManager, LessonManager, SettingsManager):
    def __init__(self):
        super().__init__()
