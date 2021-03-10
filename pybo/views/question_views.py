from sqlalchemy import func, nullslast  #p345

from flask import Blueprint         #p44
from flask import render_template   #p67
from flask import url_for, request, g, flash, current_app  #p76,102,172,184,345
from datetime import datetime
from werkzeug.utils import redirect

from .. import db
from ..models import Question, Answer, User, question_voter     #p246, 250
from ..forms import QuestionForm    #p98
from ..forms import AnswerForm      #p112

from ..views.auth_views import login_required       #p174

bp = Blueprint('question', __name__, url_prefix='/question')    #p75

def _nullslast(obj):
    if current_app.config['SQLALCHEMY_DATABASE_URI'].startswith("sqlite"):
        return obj
    else:
        return nullslast(obj)


@bp.route('/list/')     #p124, 246 
def _list():
    #page = request.args.get('page', type=int, default=1)    #페이징 
    #question_list = Question.query.order_by(Question.create_date.desc())
    #question_list = question_list.paginate(page, per_page=10)
    #return render_template('question/question_list.html', question_list=question_list)

    # 입력 파라미터
    page = request.args.get('page', type=int, default=1)
    kw = request.args.get('kw', type=str, default='')
    so = request.args.get('so', type=str, default='recent')

    # 정렬, p250
    if so == 'recommend':
        sub_query = db.session.query(question_voter.c.question_id, func.count('*').label('num_voter')) \
            .group_by(question_voter.c.question_id).subquery()
        question_list = Question.query \
            .outerjoin(sub_query, Question.id == sub_query.c.question_id) \
            .order_by(_nullslast(sub_query.c.num_voter.desc()), Question.create_date.desc())
    elif so == 'popular':
        sub_query = db.session.query(Answer.question_id, func.count('*').label('num_answer')) \
            .group_by(Answer.question_id).subquery()
        question_list = Question.query \
            .outerjoin(sub_query, Question.id == sub_query.c.question_id) \
            .order_by(_nullslast(sub_query.c.num_answer.desc()), Question.create_date.desc())
    else:  # recent, 최근 질문 
        question_list = Question.query.order_by(Question.create_date.desc())

    # 조회, p246
    if kw:
        search = '%%{}%%'.format(kw)
        sub_query = db.session.query(Answer.question_id, Answer.content, User.userid) \
            .join(User, Answer.user_id == User.idx).subquery()
        question_list = question_list \
            .join(User) \
            .outerjoin(sub_query, sub_query.c.question_id == Question.id) \
            .filter(Question.subject.ilike(search) |  # 질문제목
                    Question.content.ilike(search) |  # 질문내용
                    User.userid.ilike(search) |  # 질문작성자
                    sub_query.c.content.ilike(search) |  # 답변내용
                    sub_query.c.userid.ilike(search)  # 답변작성자
                    ) \
            .distinct()

    # 페이징, p246
    question_list = question_list.paginate(page, per_page=10)
    return render_template('question/question_list.html', question_list=question_list, page=page, kw=kw, so=so)



@bp.route('/detail/<int:question_id>/')
def detail(question_id):
    form = AnswerForm()     #p112
    question = Question.query.get_or_404(question_id)   #p74, 해당 데이터를 찾을 수 없는 경우 404 페이지 출력 
    return render_template('question/question_detail.html', question=question, form=form)   #p112


@bp.route('/create/', methods=('GET','POST'))   #p98, 101, 102
@login_required     #p174
def create():
    form = QuestionForm()

    if request.method == 'POST' and form.validate_on_submit():  #p102
        question = Question(subject=form.subject.data, content=form.content.data, 
            create_date=datetime.now(), user=g.user)    #p172
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('main.index'))  #POST 방식 요청이면 데이터 DB저장 후 질문목록 페이지로 이동 

    return render_template('question/question_form.html', form=form)    #GET 방식 요청이면 질문등록 페이지 렌더링 


#p184, 질문 수정하기 
@bp.route('/modify/<int:question_id>', methods=('GET', 'POST'))
@login_required
def modify(question_id):
    question = Question.query.get_or_404(question_id)

    if g.user != question.user:
        flash('수정권한이 없습니다')
        return redirect(url_for('question.detail', question_id=question_id))

    if request.method == 'POST':            #수정 후 저장
        form = QuestionForm()               #p98

        if form.validate_on_submit():
            form.populate_obj(question)
            question.modify_date = datetime.now()  #수정일시 저장
            db.session.commit()
            return redirect(url_for('question.detail', question_id=question_id))
    else:                                   #수정, GET 
        form = QuestionForm(obj=question)

    return render_template('question/question_form.html', form=form)


#p189, 질문 삭제하기 
@bp.route('/delete/<int:question_id>')
@login_required
def delete(question_id):
    question = Question.query.get_or_404(question_id)

    if g.user != question.user:
        flash('삭제권한이 없습니다')
        return redirect(url_for('question.detail', question_id=question_id))

    db.session.delete(question)
    db.session.commit()
    return redirect(url_for('question._list'))

    
