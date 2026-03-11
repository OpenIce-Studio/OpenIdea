'''
轮次模型
'''
from datetime import datetime
from app import db


class Round(db.Model):
    '''
    轮次模型

    Attributes:
        id (int): 轮次ID
        book_id (int): 所属书籍ID
        round_number (int): 轮次编号
        status (str): 状态（writing: 续写中, voting: 投票中, completed: 已完成）
        created_at (datetime): 创建时间
        voting_started_at (datetime): 投票开始时间
        completed_at (datetime): 完成时间
    '''
    __tablename__ = 'rounds'

    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    round_number = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='writing')  # writing, voting, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    voting_started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)

    # 关联关系
    submissions = db.relationship('Submission', backref='round', lazy='dynamic')
    winning_submission_id = db.Column(db.Integer, db.ForeignKey('submissions.id'))
    winning_submission = db.relationship('Submission', foreign_keys=[winning_submission_id])

    def to_dict(self) -> dict:
        '''
        转换为字典

        Returns:
            dict: 轮次信息字典
        '''
        return {
            'id': self.id,
            'book_id': self.book_id,
            'round_number': self.round_number,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'voting_started_at': self.voting_started_at.isoformat() if self.voting_started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'submission_count': self.submissions.count(),
            'winning_submission_id': self.winning_submission_id
        }

    def __repr__(self) -> str:
        return f'<Round {self.round_number} of Book {self.book_id}>'
