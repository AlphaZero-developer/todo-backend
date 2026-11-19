from sqlalchemy.orm import Session
from app.repositories.task import TaskRepository
from app.schemas.task import TaskSchema, TaskCreateSchema, TaskUpdateSchema
from app.cache.redis import RedisCacheBackend
from app.core.config import get_settings

settings = get_settings()


class TaskNotFound(Exception):
    """Задача не найдена в БД"""


class TaskService:
    def __init__(
        self,
        db: Session,
        cache_redis_url: str,
    ) -> None:
        self.db = db
        self.task_repository = TaskRepository(db)
        self.cache = RedisCacheBackend(cache_redis_url, settings.cache_ttl_seconds)
        self.cache_tasks_key = settings.cache_tasks_key

    def list_tasks(self) -> list[TaskSchema]:
        cached_tasks = self.cache.get(self.cache_tasks_key)
        if cached_tasks is not None:
            return cached_tasks

        tasks_orm = self.task_repository.get_all()

        task_read = [TaskSchema.model_validate(task) for task in tasks_orm]
        tasks_for_cache = [task.model_dump() for task in task_read]
        self.cache.set(self.cache_tasks_key, tasks_for_cache)

        return task_read

    def create_task(self, task_create: TaskCreateSchema) -> TaskSchema:

        self.cache.delete(self.cache_tasks_key)

        task_orm = self.task_repository.create(task_create.title)
        self.db.commit()
        return TaskSchema.model_validate(task_orm)

    def update_task(self, task_id: str, task_update: TaskUpdateSchema) -> TaskSchema:

        self.cache.delete(self.cache_tasks_key)

        task_for_update = self.task_repository.get_by_id(task_id=task_id)

        if not task_for_update:
            raise TaskNotFound(f"Задача не найдена с таким id: {task_id}")

        if task_update.title is not None:
            task_for_update.title = task_update.title
        if task_update.completed is not None:
            task_for_update.completed = task_update.completed

        self.db.commit()
        return TaskSchema.model_validate(task_for_update)

    def delete_task(self, task_id: str) -> None:

        self.cache.delete(self.cache_tasks_key)

        task_for_delete = self.task_repository.get_by_id(task_id)

        if not task_for_delete:
            raise TaskNotFound(f"Задача не найдена с таким id: {task_id}")

        self.task_repository.delete(task_for_delete)
        self.db.commit()
