'''
续写提交模型
'''
from datetime import datetime
from app import db


class Submission(db.Model):
    '''
    续写提交模型

    Attributes:
        id (int): 提交ID
        round_id (int): 所属轮次ID
        author_id (int): 作者ID
        content (str): 续写内容
        vote_count (int): 得票数
        created_at (datetime): 创建时间
    '''
    __tablename__ = 'submissions'

    id = db.Column(db.Integer, primary_key=True)
    round_id = db.Column(db.Integer, db.ForeignKey('rounds.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    vote_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        '''
        转换为字典

        Returns:
            dict: 提交信息字典
        '''
        return {
            'id': self.id,
            'round_id': self.round_id,
            'author_id': self.author_id,
            'author_name': self.author.username if self.author else None,
            'content': self.content,
            'vote_count': self.vote_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self) -> str:
        return f'<Submission {self.id} by User {self.author_id}>'
