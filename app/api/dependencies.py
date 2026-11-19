from sqlalchemy.orm import Session
from app.services.task import TaskService
from app.db.sessions import get_db
from fastapi import Depends
from app.core.config import get_settings

settings = get_settings()


def get_task_service(db: Session = Depends(get_db)):
    """Функция для инъекции зависимости Task Service"""
    return TaskService(db, settings.REDIS_URL)
