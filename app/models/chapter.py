'''
正史章节模型
'''
from datetime import datetime
from app import db


class Chapter(db.Model):
    '''
    正史章节模型（投票胜出的续写内容）

    Attributes:
        id (int): 章节ID
        book_id (int): 所属书籍ID
        round_id (int): 对应轮次ID
        author_id (int): 作者ID
        content (str): 章节内容
        chapter_number (int): 章节编号
        created_at (datetime): 创建时间
    '''
    __tablename__ = 'chapters'

    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    round_id = db.Column(db.Integer, db.ForeignKey('rounds.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    chapter_number = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        '''
        转换为字典

        Returns:
            dict: 章节信息字典
        '''
        return {
            'id': self.id,
            'book_id': self.book_id,
            'round_id': self.round_id,
            'author_id': self.author_id,
            'author_name': self.author.username if self.author else None,
            'content': self.content,
            'chapter_number': self.chapter_number,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self) -> str:
        return f'<Chapter {self.chapter_number} of Book {self.book_id}>'
