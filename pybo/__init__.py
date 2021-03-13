from flask import Flask, render_template
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flaskext.markdown import Markdown  # p232
from sqlalchemy import MetaData

import config

naming_convention = {  # p159
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
db = SQLAlchemy(metadata=MetaData(naming_convention=naming_convention))
migrate = Migrate()


def page_not_found(e):  # p323, 오류404 처리페이지
    return render_template('404.html'), 404


def Bad_Request(e):
    return render_template('400.html'), 400


def Request_Entity_Too_Large(e):
    return render_template('413.html'), 413


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
    # 다른 파일에서 app.config['UPLOAD_EXTENSIONS'] 인식하는 방법 필요
    app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']

    # ORM, p159
    db.init_app(app)
    if app.config['SQLALCHEMY_DATABASE_URI'].startswith("sqlite"):
        migrate.init_app(app, db, render_as_batch=True)
    else:
        migrate.init_app(app, db)
    from . import models

    # 블루프린트
    # p76,82,145,202,216
    from .views import main_views, question_views, answer_views, auth_views, comment_views, vote_views

    app.register_blueprint(main_views.bp)
    app.register_blueprint(question_views.bp)
    app.register_blueprint(answer_views.bp)
    app.register_blueprint(auth_views.bp)
    app.register_blueprint(comment_views.bp)
    app.register_blueprint(vote_views.bp)  # p216

    # 필터, p131
    from .filter import format_datetime
    app.jinja_env.filters['datetime'] = format_datetime

    # markdown, p232
    Markdown(app, extensions=['nl2br', 'fenced_code'])

    # 오류페이지, p323
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(400, Bad_Request)
    app.register_error_handler(413, Request_Entity_Too_Large)

    return app
