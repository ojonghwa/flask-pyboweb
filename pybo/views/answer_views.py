from datetime import datetime       #p80
from flask import Blueprint, url_for, request, render_template, g, flash   #p171,191
from werkzeug.utils import redirect

from .. import db
from ..forms import AnswerForm
from ..models import Question, Answer

from ..views.auth_views import login_required       #p174

bp = Blueprint('answer', __name__, url_prefix='/answer')    #p81


@bp.route('/create/<int:question_id>', methods=('POST',))
@login_required     #p174
def create(question_id):
    form = AnswerForm()
    question = Question.query.get_or_404(question_id)

    if form.validate_on_submit():               #p111
        content = request.form['content']       #p81
        answer = Answer(question=question, content=content, 
            create_date=datetime.now(), user=g.user)     #p82,172
        db.session.add(answer)
        db.session.commit()

        return redirect('{}#answer_{}'.format(
            url_for('question.detail', question_id=question_id), answer.id)) #p224, 앵커로 이동

    return render_template('question/question_detail.html', question=question, form=form)


#p191, 답변 수정 
@bp.route('/modify/<int:answer_id>', methods=('GET', 'POST'))   
@login_required
def modify(answer_id):
    answer = Answer.query.get_or_404(answer_id)

    if g.user != answer.user:
        flash('수정권한이 없습니다')
        return redirect(url_for('question.detail', question_id=answer.question.id))

    if request.method == "POST":
        form = AnswerForm()
        if form.validate_on_submit():
            form.populate_obj(answer)
            answer.modify_date = datetime.now()  # 수정일시 저장
            db.session.commit()
            return redirect('{}#answer_{}'.format(
                url_for('question.detail', question_id=answer.question.id), answer.id))  #p224, 앵커로 이동
    else:
        form = AnswerForm(obj=answer)

    return render_template('answer/answer_form.html', answer=answer, form=form)


#p193, 답변 삭제 
@bp.route('/delete/<int:answer_id>')
@login_required
def delete(answer_id):
    answer = Answer.query.get_or_404(answer_id)
    question_id = answer.question.id
    if g.user != answer.user:
        flash('삭제권한이 없습니다')
    else:
        db.session.delete(answer)
        db.session.commit()

    return redirect(url_for('question.detail', question_id=question_id))


