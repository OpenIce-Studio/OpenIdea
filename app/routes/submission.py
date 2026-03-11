'''
续写提交路由
'''
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.book import Book
from app.models.round import Round
from app.models.submission import Submission

submission_bp = Blueprint('submission', __name__)


@submission_bp.route('/round/<int:round_id>', methods=['GET'])
def get_submissions_by_round(round_id: int):
    '''
    获取某轮的所有提交

    Args:
        round_id (int): 轮次ID

    Returns:
        JSON: 提交列表
    '''
    round_obj = Round.query.get(round_id)
    if not round_obj:
        return jsonify({'error': '轮次不存在'}), 404
    
    submissions = Submission.query.filter_by(round_id=round_id).order_by(Submission.vote_count.desc()).all()
    
    return jsonify({
        'submissions': [submission.to_dict() for submission in submissions]
    }), 200


@submission_bp.route('', methods=['POST'])
@jwt_required()
def create_submission():
    '''
    提交续写

    Returns:
        JSON: 创建结果
    '''
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('round_id') or not data.get('content'):
        return jsonify({'error': '请提供轮次ID和续写内容'}), 400
    
    round_id = data['round_id']
    round_obj = Round.query.get(round_id)
    
    if not round_obj:
        return jsonify({'error': '轮次不存在'}), 404
    
    # 检查轮次是否还在续写阶段
    if round_obj.status != 'writing':
        return jsonify({'error': '该轮次已结束续写'}), 400
    
    # 检查用户是否已经提交过
    existing = Submission.query.filter_by(round_id=round_id, author_id=user_id).first()
    if existing:
        return jsonify({'error': '您已提交过续写，每轮只能提交一次'}), 400
    
    # 创建提交
    submission = Submission(
        round_id=round_id,
        author_id=user_id,
        content=data['content']
    )
    db.session.add(submission)
    db.session.commit()
    
    return jsonify({
        'message': '提交成功',
        'submission': submission.to_dict()
    }), 201


@submission_bp.route('/<int:submission_id>', methods=['PUT'])
@jwt_required()
def update_submission(submission_id: int):
    '''
    更新续写内容

    Args:
        submission_id (int): 提交ID

    Returns:
        JSON: 更新结果
    '''
    user_id = get_jwt_identity()
    submission = Submission.query.get(submission_id)
    
    if not submission:
        return jsonify({'error': '提交不存在'}), 404
    
    if submission.author_id != user_id:
        return jsonify({'error': '无权修改此提交'}), 403
    
    # 检查轮次是否还在续写阶段
    round_obj = Round.query.get(submission.round_id)
    if round_obj.status != 'writing':
        return jsonify({'error': '该轮次已结束续写，无法修改'}), 400
    
    data = request.get_json()
    
    if data.get('content'):
        submission.content = data['content']
    
    db.session.commit()
    
    return jsonify({
        'message': '更新成功',
        'submission': submission.to_dict()
    }), 200


@submission_bp.route('/<int:submission_id>', methods=['DELETE'])
@jwt_required()
def delete_submission(submission_id: int):
    '''
    删除续写

    Args:
        submission_id (int): 提交ID

    Returns:
        JSON: 删除结果
    '''
    user_id = get_jwt_identity()
    submission = Submission.query.get(submission_id)
    
    if not submission:
        return jsonify({'error': '提交不存在'}), 404
    
    if submission.author_id != user_id:
        return jsonify({'error': '无权删除此提交'}), 403
    
    # 检查轮次是否还在续写阶段
    round_obj = Round.query.get(submission.round_id)
    if round_obj.status != 'writing':
        return jsonify({'error': '该轮次已结束续写，无法删除'}), 400
    
    db.session.delete(submission)
    db.session.commit()
    
    return jsonify({'message': '删除成功'}), 200


@submission_bp.route('/start-voting/<int:round_id>', methods=['POST'])
@jwt_required()
def start_voting(round_id: int):
    '''
    开始投票阶段

    Args:
        round_id (int): 轮次ID

    Returns:
        JSON: 操作结果
    '''
    user_id = get_jwt_identity()
    round_obj = Round.query.get(round_id)
    
    if not round_obj:
        return jsonify({'error': '轮次不存在'}), 404
    
    # 检查书籍创建者权限
    book = Book.query.get(round_obj.book_id)
    if book.creator_id != user_id:
        return jsonify({'error': '只有书籍创建者可以开启投票'}), 403
    
    if round_obj.status != 'writing':
        return jsonify({'error': '该轮次不在续写阶段'}), 400
    
    # 检查是否有提交
    submission_count = Submission.query.filter_by(round_id=round_id).count()
    if submission_count == 0:
        return jsonify({'error': '没有续写提交，无法开启投票'}), 400
    
    # 更新轮次状态
    round_obj.status = 'voting'
    round_obj.voting_started_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'message': '投票阶段已开启',
        'round': round_obj.to_dict()
    }), 200
