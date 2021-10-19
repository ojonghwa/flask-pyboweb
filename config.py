import os

BASE_DIR = os.path.dirname(__file__)

SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(os.path.join(BASE_DIR, 'pybo.db'))
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = "dev"

#SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(
#    user='dbmasteruser', pw='abcd',
#    url='ap-northeast-2.rds.amazonaws.com',
#    db='flask_pybo')
