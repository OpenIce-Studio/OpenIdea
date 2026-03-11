'''
Flask应用工厂
'''
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app.config import config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
jwt = JWTManager()


def create_app(config_name: str = 'default') -> Flask:
    '''
    创建Flask应用实例

    Args:
        config_name (str): 配置名称，可选值为 'development', 'production', 'default'

    Returns:
        Flask: Flask应用实例
    '''
    app = Flask(__name__,
                template_folder='../templates',
                static_folder='../static')
    app.config.from_object(config[config_name])

    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    jwt.init_app(app)

    # 注册蓝图
    from app.routes.auth import auth_bp
    from app.routes.book import book_bp
    from app.routes.submission import submission_bp
    from app.routes.vote import vote_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(book_bp, url_prefix='/api/book')
    app.register_blueprint(submission_bp, url_prefix='/api/submission')
    app.register_blueprint(vote_bp, url_prefix='/api/vote')

    # 注册页面路由
    from app.routes.pages import pages_bp
    app.register_blueprint(pages_bp)

    # 创建数据库表
    with app.app_context():
        db.create_all()

    return app
