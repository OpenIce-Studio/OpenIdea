'''
书籍模型
'''
from datetime import datetime
from app import db


class Book(db.Model):
    '''
    书籍模型

    Attributes:
        id (int): 书籍ID
        title (str): 书籍标题
        opening (str): 开头内容
        creator_id (int): 创建者ID
        status (str): 状态（active: 进行中, completed: 已完结）
        created_at (datetime): 创建时间
    '''
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    opening = db.Column(db.Text, nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='active')  # active, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关联关系
    rounds = db.relationship('Round', backref='book', lazy='dynamic', 
                             order_by='Round.round_number')
    chapters = db.relationship('Chapter', backref='book', lazy='dynamic')

    def to_dict(self) -> dict:
        '''
        转换为字典

        Returns:
            dict: 书籍信息字典
        '''
        return {
            'id': self.id,
            'title': self.title,
            'opening': self.opening,
            'creator_id': self.creator_id,
            'creator_name': self.creator.username if self.creator else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'current_round': self.get_current_round_number()
        }

    def get_current_round_number(self) -> int:
        '''
        获取当前轮次编号

        Returns:
            int: 当前轮次编号
        '''
        current_round = self.rounds.filter_by(status='writing').first()
        if current_round:
            return current_round.round_number
        return 0

    def __repr__(self) -> str:
        return f'<Book {self.title}>'
