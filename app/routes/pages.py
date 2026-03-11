'''
页面路由
'''
from flask import Blueprint, render_template

pages_bp = Blueprint('pages', __name__)


@pages_bp.route('/')
def index():
    '''
    首页

    Returns:
        HTML: 首页模板
    '''
    return render_template('index.html')


@pages_bp.route('/login')
def login():
    '''
    登录页面

    Returns:
        HTML: 登录页面模板
    '''
    return render_template('login.html')


@pages_bp.route('/register')
def register():
    '''
    注册页面

    Returns:
        HTML: 注册页面模板
    '''
    return render_template('register.html')


@pages_bp.route('/create-book')
def create_book():
    '''
    创建书籍页面

    Returns:
        HTML: 创建书籍页面模板
    '''
    return render_template('create_book.html')


@pages_bp.route('/book/<int:book_id>')
def book_detail(book_id: int):
    '''
    书籍详情页面

    Args:
        book_id (int): 书籍ID

    Returns:
        HTML: 书籍详情页面模板
    '''
    return render_template('book_detail.html', book_id=book_id)


@pages_bp.route('/book/<int:book_id>/write')
def write_submission(book_id: int):
    '''
    续写页面

    Args:
        book_id (int): 书籍ID

    Returns:
        HTML: 续写页面模板
    '''
    return render_template('write_submission.html', book_id=book_id)


@pages_bp.route('/book/<int:book_id>/vote')
def vote(book_id: int):
    '''
    投票页面

    Args:
        book_id (int): 书籍ID

    Returns:
        HTML: 投票页面模板
    '''
    return render_template('vote.html', book_id=book_id)
