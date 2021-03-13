from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField
from wtforms.fields.html5 import EmailField  # p142
from wtforms.validators import DataRequired, Length, EqualTo, Email  # p142


class QuestionForm(FlaskForm):  # p98
    subject = StringField('제목', validators=[DataRequired('내용은 필수입력 항목입니다.')])
    content = TextAreaField('내용', validators=[DataRequired('내용은 필수입력 항목입니다.')])


class AnswerForm(FlaskForm):  # p110
    content = TextAreaField('내용', validators=[DataRequired('내용은 필수입력 항목입니다.')])


class UserCreateForm(FlaskForm):  # p142
    userid = StringField('사용자ID', validators=[
                         DataRequired(), Length(min=3, max=25)])
    password1 = PasswordField('비밀번호', validators=[
        DataRequired(), EqualTo('password2', '비밀번호가 일치하지 않습니다')])
    password2 = PasswordField('비밀번호확인', validators=[DataRequired()])
    email = EmailField('이메일', [DataRequired(), Email()])
    phone = StringField('전화번호', validators=[
                        DataRequired(), Length(min=11, max=35)])


class UserLoginForm(FlaskForm):  # p150
    userid = StringField('사용자ID', validators=[
                         DataRequired(), Length(min=3, max=25)])
    password = PasswordField('비밀번호', validators=[DataRequired()])


class CommentForm(FlaskForm):  # p201, 댓글 등록
    content = TextAreaField('내용', validators=[DataRequired()])
