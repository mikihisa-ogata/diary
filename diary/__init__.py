import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# flaskのインスタンス生成
app = Flask(__name__)

# 設定
app.config["SECRET_KEY"] = "mysecretkey"
basedir = os.path.abspath(os.path.dirname(__file__))
uri = os.environ.get("DATABASE_URL")
if uri:
    if uri.startswith(
        "postgres://"
    ):  # heroku上で実行する場合、uriのデフォルトがpostgres://になっているのでそれをpostgresql://に置き換える
        uri = uri.replace("postgres://", "postgresql://", 1)
        app.config["SQLALCHEMY_DATABASE_URI"] = uri
else:  # ローカル上で実行する場合 ユーザ名=postgres, password=20000911
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:20000911@localhost"
# データベースの変更履歴 => False
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# SQLAlchemyのインスタンス生成 Migrate:「python=>実際のdatebase」の変換
db = SQLAlchemy(app)
Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "users.login"  # ログインしていないユーザーをloginページに飛ばす


def localize_callback(*args, **kwargs):  # ログインしていないユーザーに対して表示するメッセージの設定
    return "このページにアクセスするにはログインが必要です"


login_manager.localize_callback = localize_callback

from diary.main.views import main  # diary/main/views => main
from diary.users.views import users  # diary/users/views => users
from diary.error_pages.handlers import (
    error_pages,
)  # diary/error_pages/handlers => error_pages

app.register_blueprint(main)  # (Blueprintのインスタンス名).Blueprint_blueprint(○○.py)
app.register_blueprint(users)  # Blueprintの有効化、登録
app.register_blueprint(error_pages)
