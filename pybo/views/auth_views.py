import functools
import imghdr
import os
import random
from flask import Blueprint, url_for, render_template, flash, abort
from flask import request, session, g, current_app  # p150
from werkzeug.security import generate_password_hash, check_password_hash  # p150
from werkzeug.utils import redirect, secure_filename

# Flask context globals
# current_app : Application context - The application instance for the active application.
# g : Application context - An object that the application can use for temporary storage during the handling of a request. This variable is reset with each request.
# request : Request context - The request object, which encapsulates the contents of a HTTP request sent by the client.
# session : Request context - The user session, a dictionary that the application can use to store values that are remembered between requests

from .. import db
from ..forms import UserCreateForm, UserLoginForm  # p142,150
from ..models import User  # p140

bp = Blueprint('auth', __name__, url_prefix='/auth')


# p143, 회원가입 화면뷰
@bp.route('/signup/', methods=('GET', 'POST'))  # URL /signup/ 과 연결된 함수
def signup():
    form = UserCreateForm()  # p142
    # POST방식 요청에는 계정등록을, GET방식 요청에는 계정등록을 하는 템플릿을 렌더링
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


# p151, 로그인 라우트
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


# p155, 모든 라우트 함수보다 먼저 load_logged_in_user() 함수가 실행되도록 함
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get(user_id)  # 플라스크 컨택스트 변수, 전체 글로벌 변수


# p157, 로그아웃 라우트
@bp.route('/logout/')
def logout():
    session.clear()
    return redirect(url_for('main.index'))


# p174, 로그인 상태관리 데코레이터 함수
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view


# 이미지파일 업로드시 헤더내용 검사하여 올바른 파일인지 확인
def validate_image(stream):
    header = stream.read(512)
    stream.seek(0)
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + (format if format != 'jpeg' else 'jpg')


# ojonghwa, 2021.3.12
# 로그인 사용자 프로필 소개 페이지 및 사진 업로드
@bp.route('/profile/', methods=('GET', 'POST'))
def profile():
    if g.user is None:
        return redirect(url_for('auth.login'))
    else:
        if request.method == 'POST':
            uploaded_file = request.files['file']

            #filename = uploaded_file.filename
            filename = secure_filename(
                uploaded_file.filename)  # 파일 디렉터리 변경 저장 차단

            if filename != '':
                file_ext = os.path.splitext(filename)[1]  # DB User 저장

                # 파일용량 검사, 파일 확장자 조사, -> 파일 헤더 조사 필요
                # if file_ext not in ['.jpg', '.png', 'gif'] or file_ext != validate_image(uploaded_file.stream):
                if file_ext not in current_app.config['UPLOAD_EXTENSIONS']:
                    abort(400)  # 400 오류발생, from flask import abort

                #uploaded_file.save('pybo/static/uploads/' + uploaded_file.filename)
                uploaded_file.save('pybo/static/uploads/' +
                                   g.user.userid + '.jpg')

        file = g.user.userid + '.jpg'
        # 캐시방지용 random 함수 사용
        return render_template('auth/profile.html', image_file=file, ver=random.random())
