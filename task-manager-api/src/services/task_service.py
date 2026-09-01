from datetime import datetime, timezone
from src.config.database import db
from src.models.task_model import Task
from src.models.user_model import User
from src.models.category_model import Category

class TaskService:
    @staticmethod
    def get_all_tasks():
        tasks = Task.query.all()
        result = []
        now = datetime.now(timezone.utc)

        # Busca usuários e categorias em mapa para evitar N+1
        users_map = {u.id: u.name for u in User.query.all()}
        cats_map = {c.id: c.name for c in Category.query.all()}

        for t in tasks:
            task_data = t.to_dict()
            task_data['overdue'] = t.is_overdue()
            task_data['user_name'] = users_map.get(t.user_id)
            task_data['category_name'] = cats_map.get(t.category_id)
            result.append(task_data)

        return result

    @staticmethod
    def search_tasks(query='', status='', priority='', user_id=''):
        tasks = Task.query
        if query:
            tasks = tasks.filter(
                db.or_(
                    Task.title.like(f'%{query}%'),
                    Task.description.like(f'%{query}%')
                )
            )
        if status:
            tasks = tasks.filter(Task.status == status)
        if priority:
            tasks = tasks.filter(Task.priority == int(priority))
        if user_id:
            tasks = tasks.filter(Task.user_id == int(user_id))

        results = tasks.all()
        return [t.to_dict() for t in results]

    @staticmethod
    def get_stats():
        total = Task.query.count()
        pending = Task.query.filter_by(status='pending').count()
        in_progress = Task.query.filter_by(status='in_progress').count()
        done = Task.query.filter_by(status='done').count()
        cancelled = Task.query.filter_by(status='cancelled').count()

        all_tasks = Task.query.all()
        overdue_count = sum(1 for t in all_tasks if t.is_overdue())

        return {
            'total': total,
            'pending': pending,
            'in_progress': in_progress,
            'done': done,
            'cancelled': cancelled,
            'overdue': overdue_count,
            'completion_rate': round((done / total) * 100, 2) if total > 0 else 0
        }
