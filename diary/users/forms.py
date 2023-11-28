from flask_wtf import FlaskForm
from wtforms import ValidationError, StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Email
from diary.models import User


class LoginForm(FlaskForm):  # LoginForm作成 FlaskFormの継承 Flask-WTF拡張機能 入力フィールドで使用
    email = StringField("Email", validators=[DataRequired()])
    password = StringField("Password", validators=[DataRequired()])
    submit = SubmitField("ログイン")


class RegistrationForm(FlaskForm):  # RegistrationForm作成
    email = StringField("メールアドレス", validators=[DataRequired()])
    username = StringField("ユーザー名", validators=[DataRequired()])
    password = PasswordField(
        "パスワード",
        validators=[DataRequired(), EqualTo("pass_confirm", message="パスワードが一致していません")],
    )
    pass_confirm = PasswordField("パスワード（確認）", validators=[DataRequired()])
    submit = SubmitField("登録")

    def validate_username(self, field):  # usernameのバリデーション(フォームの入力データの妥当性をチェックする)
        if User.query.filter_by(username=field.data).first():
            raise ValidationError("入力されたユーザー名は既にに登録されています。")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("入力されたメールアドレスは既に登録されています。")


class UpdateUserForm(FlaskForm):  # UpdateUserForm作成
    email = StringField("メールアドレス", validators=[DataRequired()])
    username = StringField("ユーザー名", validators=[DataRequired()])
    password = PasswordField(
        "パスワード", validators=[EqualTo("pass_confirm", message="パスワードが一致していません。")]
    )
    pass_confirm = PasswordField("パスワード（確認）")
    submit = SubmitField("更新")

    def __init__(self, user_id, *args, **kwargs):
        super(UpdateUserForm, self).__init__(*args, **kwargs)
        self.id = user_id
