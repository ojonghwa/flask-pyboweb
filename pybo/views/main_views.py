from flask import Blueprint     #p44
from flask import url_for       #p76 
from werkzeug.utils import redirect     #p76

bp = Blueprint('main', __name__, url_prefix='/')


@bp.route('/')
def index():
    return redirect(url_for('question._list'))


@bp.route('/hello')
def hello_pybo():
    return 'Hello, World!'
