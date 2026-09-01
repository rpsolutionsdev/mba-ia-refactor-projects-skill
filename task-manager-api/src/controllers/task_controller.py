import logging
from datetime import datetime, timezone
from flask import request, jsonify
from src.config.database import db
from src.config.settings import settings
from src.models.task_model import Task
from src.models.user_model import User
from src.models.category_model import Category
from src.services.task_service import TaskService
from src.services.notification_service import notification_service

logger = logging.getLogger(__name__)

class TaskController:
    @staticmethod
    def get_tasks():
        try:
            tasks = TaskService.get_all_tasks()
            return jsonify(tasks), 200
        except Exception as e:
            logger.error(f"Erro ao listar tarefas: {e}", exc_info=True)
            return jsonify({'error': 'Erro interno ao listar tarefas'}), 500

    @staticmethod
    def get_task(task_id):
        task = Task.query.get(task_id)
        if not task:
            return jsonify({'error': 'Task não encontrada'}), 404

        data = task.to_dict()
        data['overdue'] = task.is_overdue()
        return jsonify(data), 200

    @staticmethod
    def create_task():
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados inválidos'}), 400

        title = data.get('title')
        if not title:
            return jsonify({'error': 'Título é obrigatório'}), 400

        title = str(title).strip()
        if len(title) < 3:
            return jsonify({'error': 'Título muito curto'}), 400
        if len(title) > 200:
            return jsonify({'error': 'Título muito longo'}), 400

        description = data.get('description', '')
        status = data.get('status', 'pending')
        priority = data.get('priority', 3)
        user_id = data.get('user_id')
        category_id = data.get('category_id')
        due_date = data.get('due_date')
        tags = data.get('tags')

        if status not in settings.VALID_STATUSES:
            return jsonify({'error': f'Status inválido. Permitidos: {settings.VALID_STATUSES}'}), 400

        try:
            priority = int(priority)
            if priority < settings.MIN_PRIORITY or priority > settings.MAX_PRIORITY:
                return jsonify({'error': 'Prioridade deve ser entre 1 e 5'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'Prioridade inválida'}), 400

        assigned_user = None
        if user_id:
            assigned_user = User.query.get(user_id)
            if not assigned_user:
                return jsonify({'error': 'Usuário não encontrado'}), 404

        if category_id:
            cat = Category.query.get(category_id)
            if not cat:
                return jsonify({'error': 'Categoria não encontrada'}), 404

        task = Task()
        task.title = title
        task.description = description
        task.status = status
        task.priority = priority
        task.user_id = user_id
        task.category_id = category_id

        if due_date:
            try:
                task.due_date = datetime.strptime(due_date, '%Y-%m-%d')
            except ValueError:
                return jsonify({'error': 'Formato de data inválido. Use YYYY-MM-DD'}), 400

        if tags:
            task.tags = ','.join(tags) if isinstance(tags, list) else tags

        try:
            db.session.add(task)
            db.session.commit()
            logger.info(f"Task criada: {task.id} - {task.title}")

            if assigned_user:
                notification_service.notify_task_assigned(assigned_user, task)

            return jsonify(task.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao criar task: {e}", exc_info=True)
            return jsonify({'error': 'Erro ao criar task'}), 500

    @staticmethod
    def update_task(task_id):
        task = Task.query.get(task_id)
        if not task:
            return jsonify({'error': 'Task não encontrada'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados inválidos'}), 400

        if 'title' in data:
            title = str(data['title']).strip()
            if len(title) < 3:
                return jsonify({'error': 'Título muito curto'}), 400
            if len(title) > 200:
                return jsonify({'error': 'Título muito longo'}), 400
            task.title = title

        if 'description' in data:
            task.description = data['description']

        if 'status' in data:
            if data['status'] not in settings.VALID_STATUSES:
                return jsonify({'error': 'Status inválido'}), 400
            task.status = data['status']

        if 'priority' in data:
            try:
                p = int(data['priority'])
                if p < settings.MIN_PRIORITY or p > settings.MAX_PRIORITY:
                    return jsonify({'error': 'Prioridade deve ser entre 1 e 5'}), 400
                task.priority = p
            except (ValueError, TypeError):
                return jsonify({'error': 'Prioridade inválida'}), 400

        if 'user_id' in data:
            if data['user_id']:
                user = User.query.get(data['user_id'])
                if not user:
                    return jsonify({'error': 'Usuário não encontrado'}), 404
            task.user_id = data['user_id']

        if 'category_id' in data:
            if data['category_id']:
                cat = Category.query.get(data['category_id'])
                if not cat:
                    return jsonify({'error': 'Categoria não encontrada'}), 404
            task.category_id = data['category_id']

        if 'due_date' in data:
            if data['due_date']:
                try:
                    task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d')
                except ValueError:
                    return jsonify({'error': 'Formato de data inválido'}), 400
            else:
                task.due_date = None

        if 'tags' in data:
            task.tags = ','.join(data['tags']) if isinstance(data['tags'], list) else data['tags']

        task.updated_at = datetime.now(timezone.utc)

        try:
            db.session.commit()
            logger.info(f"Task atualizada: {task.id}")
            return jsonify(task.to_dict()), 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao atualizar task: {e}", exc_info=True)
            return jsonify({'error': 'Erro ao atualizar'}), 500

    @staticmethod
    def delete_task(task_id):
        task = Task.query.get(task_id)
        if not task:
            return jsonify({'error': 'Task não encontrada'}), 404

        try:
            db.session.delete(task)
            db.session.commit()
            logger.info(f"Task deletada: {task_id}")
            return jsonify({'message': 'Task deletada com sucesso'}), 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao deletar task: {e}", exc_info=True)
            return jsonify({'error': 'Erro ao deletar'}), 500

    @staticmethod
    def search_tasks():
        query = request.args.get('q', '')
        status = request.args.get('status', '')
        priority = request.args.get('priority', '')
        user_id = request.args.get('user_id', '')

        results = TaskService.search_tasks(query, status, priority, user_id)
        return jsonify(results), 200

    @staticmethod
    def task_stats():
        stats = TaskService.get_stats()
        return jsonify(stats), 200
