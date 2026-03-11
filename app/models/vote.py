'''
投票模型
'''
from datetime import datetime
from app import db


class Vote(db.Model):
    '''
    投票模型

    Attributes:
        id (int): 投票ID
        submission_id (int): 提交ID
        voter_id (int): 投票者ID
        created_at (datetime): 创建时间
    '''
    __tablename__ = 'votes'

    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submissions.id'), nullable=False)
    voter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 联合唯一约束：每个用户在每轮只能投一票
    __table_args__ = (
        db.UniqueConstraint('submission_id', 'voter_id', name='unique_vote'),
    )

    def to_dict(self) -> dict:
        '''
        转换为字典

        Returns:
            dict: 投票信息字典
        '''
        return {
            'id': self.id,
            'submission_id': self.submission_id,
            'voter_id': self.voter_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self) -> str:
        return f'<Vote by User {self.voter_id} for Submission {self.submission_id}>'
