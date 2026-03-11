'''
投票路由
'''
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.book import Book
from app.models.round import Round
from app.models.submission import Submission
from app.models.vote import Vote
from app.models.chapter import Chapter

vote_bp = Blueprint('vote', __name__)


@vote_bp.route('', methods=['POST'])
@jwt_required()
def create_vote():
    '''
    投票

    Returns:
        JSON: 投票结果
    '''
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('submission_id'):
        return jsonify({'error': '请提供提交ID'}), 400
    
    submission_id = data['submission_id']
    submission = Submission.query.get(submission_id)
    
    if not submission:
        return jsonify({'error': '提交不存在'}), 404
    
    # 获取轮次信息
    round_obj = Round.query.get(submission.round_id)
    if not round_obj or round_obj.status != 'voting':
        return jsonify({'error': '当前不在投票阶段'}), 400
    
    # 检查用户是否已在此轮次投过票
    existing_vote = db.session.query(Vote).join(Submission).filter(
        Submission.round_id == round_obj.id,
        Vote.voter_id == user_id
    ).first()
    
    if existing_vote:
        return jsonify({'error': '您已在此轮次投过票，每轮只能投一票'}), 400
    
    # 创建投票
    vote = Vote(
        submission_id=submission_id,
        voter_id=user_id
    )
    db.session.add(vote)
    
    # 更新提交的票数
    submission.vote_count += 1
    
    db.session.commit()
    
    return jsonify({
        'message': '投票成功',
        'vote': vote.to_dict()
    }), 201


@vote_bp.route('/round/<int:round_id>/my-vote', methods=['GET'])
@jwt_required()
def get_my_vote(round_id: int):
    '''
    获取当前用户在指定轮次的投票

    Args:
        round_id (int): 轮次ID

    Returns:
        JSON: 投票信息
    '''
    user_id = get_jwt_identity()
    
    vote = db.session.query(Vote).join(Submission).filter(
        Submission.round_id == round_id,
        Vote.voter_id == user_id
    ).first()
    
    if not vote:
        return jsonify({'voted': False, 'vote': None}), 200
    
    return jsonify({
        'voted': True,
        'vote': vote.to_dict()
    }), 200


@vote_bp.route('/finalize/<int:round_id>', methods=['POST'])
@jwt_required()
def finalize_round(round_id: int):
    '''
    结束投票，确定获胜的续写，创建正史章节，开启下一轮

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
        return jsonify({'error': '只有书籍创建者可以结束投票'}), 403
    
    if round_obj.status != 'voting':
        return jsonify({'error': '该轮次不在投票阶段'}), 400
    
    # 获取票数最高的提交
    winning_submission = Submission.query.filter_by(round_id=round_id)\
        .order_by(Submission.vote_count.desc())\
        .first()
    
    if not winning_submission:
        return jsonify({'error': '没有续写提交'}), 400
    
    # 处理平票情况：选择最早提交的
    top_submissions = Submission.query.filter_by(
        round_id=round_id,
        vote_count=winning_submission.vote_count
    ).order_by(Submission.created_at).all()
    
    winner = top_submissions[0]
    
    # 创建正史章节
    chapter_number = round_obj.round_number
    chapter = Chapter(
        book_id=round_obj.book_id,
        round_id=round_obj.id,
        author_id=winner.author_id,
        content=winner.content,
        chapter_number=chapter_number
    )
    db.session.add(chapter)
    
    # 更新轮次状态
    round_obj.status = 'completed'
    round_obj.completed_at = datetime.utcnow()
    round_obj.winning_submission_id = winner.id
    
    # 创建下一轮
    next_round = Round(
        book_id=round_obj.book_id,
        round_number=round_obj.round_number + 1,
        status='writing'
    )
    db.session.add(next_round)
    
    db.session.commit()
    
    return jsonify({
        'message': '投票已结束，正史章节已生成',
        'winning_submission': winner.to_dict(),
        'chapter': chapter.to_dict(),
        'next_round': next_round.to_dict()
    }), 200


@vote_bp.route('/results/<int:round_id>', methods=['GET'])
def get_vote_results(round_id: int):
    '''
    获取投票结果

    Args:
        round_id (int): 轮次ID

    Returns:
        JSON: 投票结果
    '''
    round_obj = Round.query.get(round_id)
    if not round_obj:
        return jsonify({'error': '轮次不存在'}), 404
    
    submissions = Submission.query.filter_by(round_id=round_id)\
        .order_by(Submission.vote_count.desc())\
        .all()
    
    return jsonify({
        'round': round_obj.to_dict(),
        'results': [submission.to_dict() for submission in submissions]
    }), 200
