'''
用户模型
'''
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


class User(UserMixin, db.Model):
    '''
    用户模型

    Attributes:
        id (int): 用户ID
        username (str): 用户名
        email (str): 邮箱
        password_hash (str): 密码哈希值
        created_at (datetime): 创建时间
    '''
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关联关系
    books = db.relationship('Book', backref='creator', lazy='dynamic')
    submissions = db.relationship('Submission', backref='author', lazy='dynamic')
    votes = db.relationship('Vote', backref='voter', lazy='dynamic')

    def set_password(self, password: str) -> None:
        '''
        设置密码

        Args:
            password (str): 明文密码
        '''
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        '''
        验证密码

        Args:
            password (str): 明文密码

        Returns:
            bool: 密码是否正确
        '''
        return check_password_hash(self.password_hash, password)

    def to_dict(self) -> dict:
        '''
        转换为字典

        Returns:
            dict: 用户信息字典
        '''
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self) -> str:
        return f'<User {self.username}>'


@login_manager.user_loader
def load_user(user_id: str):
    '''
    加载用户回调函数

    Args:
        user_id (str): 用户ID

    Returns:
        User: 用户对象
    '''
    return User.query.get(int(user_id))
