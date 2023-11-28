from flask import render_template, url_for, redirect, session, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from diary import db
from diary.models import User, BlogPost, BlogCategory
from diary.users.forms import RegistrationForm, LoginForm, UpdateUserForm
from diary.main.forms import BlogSearchForm
from flask import Blueprint

users = Blueprint("users", __name__)  # アプリケーションのモジュール化、第1引数が名前、第2引数が最新のモジュールの名前？


@users.route("/login", methods=["GET", "POST"])  # view関数の設定
def login():
    form = LoginForm()  # LoginForm:ログインフォームの表示と入力データの取得を可能にする。
    if form.validate_on_submit():  # 送信されたformの中身のバリデーション
        user = User.query.filter_by(
            email=form.email.data
        ).first()  # 入力されたメールアドレスに一致するメールアドレスをデータベースから探して入れる
        if user is not None:  # userが存在したら
            if user.check_password(
                form.password.data
            ):  # 入力したパスワードがuserデータベースのパスワードと一致するか
                login_user(user)
                next = request.args.get("next")  # ?
                if next == None or not next[0] == "/":  # ?
                    next = url_for(
                        "main.blog_maintenance"
                    )  # urlを指定するときはBlueprintの変数名を頭につける.url_forは関数名を指定.
                return redirect(next)
            else:
                flash("パスワードが一致しません")
        else:
            flash("入力されたユーザーは存在しません")
    return render_template("users/login.html", form=form)


@users.route("/logout")
@login_required  # ログイン必須
def logout():
    logout_user()
    return redirect(url_for("users.login"))


@users.route("/register", methods=["GET", "POST"])
@login_required
def register():  # ユーザー登録
    form = RegistrationForm()
    if not current_user.is_administrator():  # 管理者ユーザーでなければ403エラーを返す
        abort(403)
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            username=form.username.data,
            password=form.password.data,
            administrator="0",
        )  # register.htmlのフォーム => レコード作成
        db.session.add(user)
        db.session.commit()
        flash("ユーザーが登録されました")
        return redirect(url_for("users.user_maintenance"))
    return render_template("users/register.html", form=form)


@users.route("/user_maintenance")
@login_required
def user_maintenance():
    page = request.args.get("page", 1, type=int)
    users = User.query.order_by(User.id).paginate(page=page, per_page=10)
    return render_template(
        "users/user_maintenance.html", users=users
    )  # user_maintenance.htmlにusersのデータを渡す


@users.route("/<int:user_id>/account", methods=["GET", "POST"])
@login_required
def account(user_id):  # routeのuser_idが引数
    user = User.query.get_or_404(user_id)  # user_idが見つからなかったら404エラー
    if (
        user.id != current_user.id and not current_user.is_administrator()
    ):  # user.idがcurrent_user.idではない、かつ管理者でない場合 => 403
        abort(403)
    form = UpdateUserForm(user_id)  # views.pyで作成したクラスで、そこでのusername, email, password
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        if form.password.data:
            user.password = form.password.data
        db.session.commit()
        flash("ユーザーアカウントが更新されました")
        return redirect(url_for("users.user_maintenance"))
    elif request.method == "GET":
        form.username.data = user.username
        form.email.data = user.email
    return render_template("users/account.html", form=form)


@users.route("/<int:user_id>/delete", methods=["GET", "POST"])
@login_required
def delete_user(user_id):  # ユーザー削除
    if not current_user.is_administrator():
        abort(403)
    if user.is_administrator():
        flash("管理者は削除できません")
        return redirect(url_for("users.account", user_id=user_id))
    user = User.query.get_or_404(user_id)  # user_idからレコードを抽出
    db.session.delete(user)
    db.session.commit()
    flash("ユーザーアカウントが削除されました")
    return redirect(url_for("users.user_maintenance"))


@users.route("/<int:user_id>/user_posts")
@login_required
def user_posts(user_id):
    form = BlogSearchForm()
    user = User.query.filter_by(id=user_id).first_or_404()  # ユーザーの取得
    page = request.args.get("page", 1, type=int)  # ブログ記事の取得
    blog_posts = (
        BlogPost.query.filter_by(user_id=user_id)
        .order_by(BlogPost.id.desc())
        .paginate(page=page, per_page=10)
    )
    recent_blog_posts = (
        BlogPost.query.order_by(BlogPost.id.desc()).limit(5).all()
    )  # 最新記事の取得
    blog_categories = BlogCategory.query.order_by(
        BlogCategory.id.asc()
    ).all()  # カテゴリの取得

    return render_template(
        "index.html",
        blog_posts=blog_posts,
        recent_blog_posts=recent_blog_posts,
        blog_categories=blog_categories,
        user=user,
        form=form,
    )
