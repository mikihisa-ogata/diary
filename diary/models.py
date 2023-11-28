from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from datetime import datetime
from pytz import timezone
from diary import db, login_manager


@login_manager.user_loader  # login_managerのuser_loader(メソッド) セッションからユーザーをリロードする
def load_user(user_id):
    return User.query.get(user_id)


# User(class)作成,クラスの継承 db.Model(ORM（Object-Relational Mapping)):pythonコードで簡単にデータベースの操作が可能, UserMixin Flask-Login拡張機能を容易に利用できる ユーザーの認証、ログイン、セッション管理など
class User(db.Model, UserMixin):
    # table'users'を作成 カテゴリ:id,email,username,password_hash,administrator
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)  # カラムの定義  primary_key主キー
    email = db.Column(db.String(64), unique=True, index=True)  # String文字数制限 unique重複なし
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    administrator = db.Column(db.String(1))
    post = db.relationship("BlogPost", backref="author", lazy="dynamic")  # リレーションシップの設定

    # 初期設定
    def __init__(self, email, username, password, administrator):
        self.email = email
        self.username = username
        self.password = password
        self.administrator = administrator

    # print文で表示
    def __repr__(self):
        return f"UserName: {self.username}"

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # パスワードの一致確認
    @property  # デコレータ
    def password(self):
        raise AttributeError("password is a not readable attribute")  # raise:エラー処理

    @password.setter
    def password(self, password):  # パスワードハッシュ化
        self.password_hash = generate_password_hash(password)

    # 管理者権限の設定
    def is_administrator(self):
        if self.administrator == "1":
            return 1
        else:
            return 0

    def count_posts(self, userid):
        return BlogPost.query.filter_by(user_id=userid).count()


class BlogPost(db.Model):
    __tablename__ = "blog_post"  # テーブル作成
    id = db.Column(db.Integer, primary_key=True)  # 主キー
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))  # 外部キー
    category_id = db.Column(db.Integer, db.ForeignKey("blog_category.id"))  # 外部キー
    date = db.Column(db.DateTime, default=datetime.now(timezone("Asia/Tokyo")))
    title = db.Column(db.String(140))
    text = db.Column(db.Text)
    summary = db.Column(db.String(140))
    featured_image = db.Column(db.String(140))

    # 初期設定
    def __init__(self, title, text, featured_image, user_id, category_id, summary):
        self.title = title
        self.text = text
        self.featured_image = featured_image
        self.user_id = user_id
        self.category_id = category_id
        self.summary = summary

    def __repr__(self):
        return f"PostID: {self.id}, Title: {self.title}, Author: {self.author} \n"


class BlogCategory(db.Model):  # db.Modelを継承
    __tablename__ = "blog_category"
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(140))
    posts = db.relationship("BlogPost", backref="blogcategory", lazy="dynamic")
    # dynamic => 1対多

    def __init__(self, category):
        self.category = category

    def __repr__(self):
        return f"CategoryID: {self.id}, CategoryName: {self.category} \n"

    def count_posts(self, id):
        return BlogPost.query.filter_by(category_id=id).count()
