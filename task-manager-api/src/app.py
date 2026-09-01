import logging
from flask import Flask
from flask_cors import CORS
from src.config.settings import settings
from src.config.database import db
from src.routes.system_routes import system_bp
from src.routes.user_routes import user_bp
from src.routes.task_routes import task_bp
from src.routes.category_routes import category_bp
from src.routes.report_routes import report_bp
from src.middlewares.error_handler import register_error_handlers

def create_app():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = settings.SQLALCHEMY_TRACK_MODIFICATIONS
    app.config['SECRET_KEY'] = settings.SECRET_KEY

    CORS(app)
    db.init_app(app)

    with app.app_context():
        # Import models to ensure they are registered
        from src.models import user_model, task_model, category_model
        db.create_all()

    # Blueprints
    app.register_blueprint(system_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(task_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(report_bp)

    # Middleware
    register_error_handlers(app)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=settings.DEBUG, host=settings.HOST, port=settings.PORT)
