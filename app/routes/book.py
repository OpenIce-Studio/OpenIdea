'''
书籍路由
'''
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.book import Book
from app.models.round import Round
from app.models.chapter import Chapter

book_bp = Blueprint('book', __name__)


@book_bp.route('', methods=['GET'])
def get_books():
    '''
    获取书籍列表

    Returns:
        JSON: 书籍列表
    '''
    books = Book.query.order_by(Book.created_at.desc()).all()
    return jsonify({
        'books': [book.to_dict() for book in books]
    }), 200


@book_bp.route('/<int:book_id>', methods=['GET'])
def get_book(book_id: int):
    '''
    获取书籍详情

    Args:
        book_id (int): 书籍ID

    Returns:
        JSON: 书籍详情
    '''
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'error': '书籍不存在'}), 404
    
    # 获取所有正史章节
    chapters = Chapter.query.filter_by(book_id=book_id).order_by(Chapter.chapter_number).all()
    
    # 获取当前轮次
    current_round = Round.query.filter_by(book_id=book_id, status='writing').first()
    if not current_round:
        current_round = Round.query.filter_by(book_id=book_id, status='voting').first()
    
    return jsonify({
        'book': book.to_dict(),
        'chapters': [chapter.to_dict() for chapter in chapters],
        'current_round': current_round.to_dict() if current_round else None
    }), 200


@book_bp.route('', methods=['POST'])
@jwt_required()
def create_book():
    '''
    创建书籍

    Returns:
        JSON: 创建结果
    '''
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('title') or not data.get('opening'):
        return jsonify({'error': '请提供标题和开头内容'}), 400
    
    # 创建书籍
    book = Book(
        title=data['title'],
        opening=data['opening'],
        creator_id=user_id
    )
    db.session.add(book)
    db.session.flush()  # 获取book.id
    
    # 创建第一轮续写
    first_round = Round(
        book_id=book.id,
        round_number=1,
        status='writing'
    )
    db.session.add(first_round)
    db.session.commit()
    
    return jsonify({
        'message': '书籍创建成功',
        'book': book.to_dict()
    }), 201


@book_bp.route('/<int:book_id>', methods=['PUT'])
@jwt_required()
def update_book(book_id: int):
    '''
    更新书籍信息

    Args:
        book_id (int): 书籍ID

    Returns:
        JSON: 更新结果
    '''
    user_id = get_jwt_identity()
    book = Book.query.get(book_id)
    
    if not book:
        return jsonify({'error': '书籍不存在'}), 404
    
    if book.creator_id != user_id:
        return jsonify({'error': '无权修改此书籍'}), 403
    
    data = request.get_json()
    
    if data.get('title'):
        book.title = data['title']
    if data.get('status'):
        book.status = data['status']
    
    db.session.commit()
    
    return jsonify({
        'message': '更新成功',
        'book': book.to_dict()
    }), 200


@book_bp.route('/<int:book_id>', methods=['DELETE'])
@jwt_required()
def delete_book(book_id: int):
    '''
    删除书籍

    Args:
        book_id (int): 书籍ID

    Returns:
        JSON: 删除结果
    '''
    user_id = get_jwt_identity()
    book = Book.query.get(book_id)
    
    if not book:
        return jsonify({'error': '书籍不存在'}), 404
    
    if book.creator_id != user_id:
        return jsonify({'error': '无权删除此书籍'}), 403
    
    db.session.delete(book)
    db.session.commit()
    
    return jsonify({'message': '删除成功'}), 200
