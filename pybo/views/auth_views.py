  
import functools        #p174
from flask import Blueprint, url_for, render_template, flash, request, session, g  #p150
from werkzeug.security import generate_password_hash, check_password_hash   #p150
from werkzeug.utils import redirect

from .. import db
from ..forms import UserCreateForm, UserLoginForm  #p142,150
from ..models import User           #p140

bp = Blueprint('auth', __name__, url_prefix='/auth')


#p143, 회원가입 화면뷰 
@bp.route('/signup/', methods=('GET', 'POST'))      #URL /signup/ 과 연결된 함수 
def signup():
    form = UserCreateForm()     #p142
    #POST방식 요청에는 계정등록을, GET방식 요청에는 계정등록을 하는 템플릿을 렌더링  
    if request.method == 'POST' and form.validate_on_submit():
        user = User.query.filter_by(userid=form.userid.data).first()
        if not user:
            user = User(userid=form.userid.data,
                        password=generate_password_hash(form.password1.data),
                        email=form.email.data,
                        phone=form.phone.data)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('main.index'))
        else:
            flash('이미 존재하는 사용자ID 입니다.')
    return render_template('auth/signup.html', form=form)


#p151, 로그인 라우트 
@bp.route('/login/', methods=('GET', 'POST'))
def login():
    form = UserLoginForm()

    if request.method == 'POST' and form.validate_on_submit():
        error = None
        user = User.query.filter_by(userid=form.userid.data).first()
        if not user:
            error = "존재하지 않는 사용자입니다."
        elif not check_password_hash(user.password, form.password.data):
            error = "비밀번호가 올바르지 않습니다."
        if error is None:
            session.clear()
            session['user_id'] = user.idx
            return redirect(url_for('main.index'))
        flash(error)
    return render_template('auth/login.html', form=form)


#p155, 모든 라우트 함수보다 먼저 load_logged_in_user() 함수가 실행되도록 함
@bp.before_app_request       
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get(user_id)    #플라스크 컨택스트 변수, 전체 글로벌 변수


#p157, 로그아웃 라우트 
@bp.route('/logout/')
def logout():
    session.clear()
    return redirect(url_for('main.index'))


#p174, 로그인 상태관리 데코레이터 함수 
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view
    